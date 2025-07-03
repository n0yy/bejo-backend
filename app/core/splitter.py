from langchain_text_splitters import RecursiveCharacterTextSplitter


def splitter() -> RecursiveCharacterTextSplitter:
    """Create a text splitter for document processing"""
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
