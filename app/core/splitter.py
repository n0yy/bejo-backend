from langchain_text_splitters import RecursiveCharacterTextSplitter


def splitter() -> RecursiveCharacterTextSplitter:
    """Create a text splitter for document processing"""
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Adjust chunk size as needed
        chunk_overlap=200,  # Adjust overlap as needed
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
