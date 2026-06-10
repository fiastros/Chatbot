# check_chroma.py
import chromadb
from config import settings

# Connect to the local folder
client = chromadb.PersistentClient(path=settings.chroma_db_path)

# Get our collection
collection = client.get_collection("document_chunks")

# Fetch and print the number of items and a sample
count = collection.count()
print(f"Total chunks in Vector DB: {count}")

if count > 0:
    sample = collection.peek(1)
    print("\n--- Sample Document ---")
    print(sample['documents'][0])
    print("Metadata:", sample['metadatas'][0])