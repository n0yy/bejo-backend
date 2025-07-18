from qdrant_client import QdrantClient

import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

qdrant_client = QdrantClient(url=QDRANT_HOST, port=QDRANT_PORT)
