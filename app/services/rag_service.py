from qdrant_client.models import Distance, VectorParams

from langchain_docling import DoclingLoader
from langchain_qdrant import QdrantVectorStore
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.core.embeddings import embeddings
from app.core.vectorstore import qdrant_client
from app.core.splitter import splitter
from app.core.llm import llm
from app.core.memory import memory

import uuid
from datetime import datetime

COLLECTION_NAMES = [
    "bejo_knowledge_level_1",
    "bejo_knowledge_level_2",
    "bejo_knowledge_level_3",
    "bejo_knowledge_level_4",
]

CATEGORY_TO_COLLECTION = {
    "1": "bejo_knowledge_level_1",
    "2": "bejo_knowledge_level_2",
    "3": "bejo_knowledge_level_3",
    "4": "bejo_knowledge_level_4",
}


class RAGService:
    def __init__(self):
        self.setup_collections()
        self.vector_stores = {}
        self.setup_vector_stores()

    def setup_collections(self):
        """Setup Qdrant collections if they don't exist"""
        for collection_name in COLLECTION_NAMES:
            try:
                qdrant_client.get_collection(collection_name)
                print(f"Collection {collection_name} already exists")
            except Exception:
                print(f"Creating collection {collection_name}")
                qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=768,
                        distance=Distance.COSINE,
                    ),
                )

    def setup_vector_stores(self):
        """Initialize vector stores for each collection"""
        for collection_name in COLLECTION_NAMES:
            self.vector_stores[collection_name] = QdrantVectorStore(
                client=qdrant_client,
                collection_name=collection_name,
                embedding=embeddings,
            )

    def process_document(
        self, file_path: str, filename: str, category: str
    ) -> tuple[int, str]:
        """Process document and add to vector store"""
        # Load document using DoclingLoader
        loader = DoclingLoader(file_path=file_path)
        documents = loader.load()

        if not documents:
            raise ValueError("No content extracted from document")

        # Add metadata
        document_id = str(uuid.uuid4())
        for doc in documents:
            doc.metadata.update(
                {
                    "filename": filename,
                    "document_id": document_id,
                    "upload_date": datetime.now().isoformat(),
                    "file_path": file_path,
                    "category": category,
                }
            )

        # Split documents into chunks
        chunks = splitter().split_documents(documents)

        # Get appropriate vector store
        collection_name = CATEGORY_TO_COLLECTION.get(category)
        if not collection_name:
            raise ValueError(f"Invalid category: {category}")

        vector_store = self.vector_stores[collection_name]

        # Add chunks to vector store
        vector_store.add_documents(chunks)

        return len(chunks), document_id

    def create_retrieval_tool(self, category: str):
        """Create retrieval tool for specific category"""
        collection_name = CATEGORY_TO_COLLECTION.get(category)
        if not collection_name:
            raise ValueError(f"Invalid category: {category}")

        vector_store = self.vector_stores[collection_name]

        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve information related to a query from the knowledge base."""
            try:
                retrieved_docs = vector_store.similarity_search(query, k=5)
                if not retrieved_docs:
                    return "No relevant information found in the knowledge base.", []

                serialized = "\n\n".join(
                    [
                        f"Source: {doc.metadata.get('filename', 'Unknown')}\n"
                        f"Document ID: {doc.metadata.get('document_id', 'Unknown')}\n"
                        f"Content: {doc.page_content}"
                        for doc in retrieved_docs
                    ]
                )
                return serialized, retrieved_docs
            except Exception as e:
                return f"Error during retrieval: {str(e)}", []

        return retrieve

    def create_rag_graph(self, category: str):
        """Create RAG graph for specific category"""
        retrieve_tool = self.create_retrieval_tool(category)

        def query_or_respond(state: MessagesState):
            """Generate tool call for retrieval or respond directly."""
            llm_with_tools = llm.bind_tools([retrieve_tool])
            response = llm_with_tools.invoke(state["messages"])
            response.additional_kwargs["timestamp"] = datetime.utcnow().isoformat()
            return {"messages": [response]}

        def generate(state: MessagesState):
            """Generate answer using retrieved context."""
            recent_tool_messages = []
            for message in reversed(state["messages"]):
                if message.type == "tool":
                    recent_tool_messages.append(message)
                else:
                    break
            tool_messages = recent_tool_messages[::-1]

            docs_content = "\n\n".join(doc.content for doc in tool_messages)

            system_message_content = (
                "You are Bejo, a helpful AI assistant for question-answering tasks. "
                "You are known for being informative, friendly, and full of energy. "
                "Use the following pieces of retrieved context to answer the question. "
                "If you don't know the answer based on the context, say that you don't know. "
                "Respond in markdown format with relevant emojis to make the answer more engaging. "
                "Keep your answers concise yet helpful."
                "Note: Always respond in the same language the current user uses.\n\n"
                f"Context:\n{docs_content}"
            )

            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]

            prompt = [SystemMessage(system_message_content)] + conversation_messages
            response = llm.invoke(prompt)
            response.additional_kwargs["timestamp"] = datetime.utcnow().isoformat()
            return {"messages": [response]}

        # Build graph
        graph_builder = StateGraph(MessagesState)
        tools = ToolNode([retrieve_tool])

        graph_builder.add_node("query_or_respond", query_or_respond)
        graph_builder.add_node("tools", tools)
        graph_builder.add_node("generate", generate)

        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile(checkpointer=memory)


rag_service = RAGService()
