import chromadb
from utils.rag import embed_data

client = chromadb.PersistentClient(path="../chroma_db")

collection = client.get_or_create_collection("courses")

print("Initial")
print(collection)
print(collection.count(), end="\n")

client.delete_collection(name="courses")

try:
    print("Deleted")
    print(collection)
    print(collection.count(), end="\n")
except:
    print("No collection", end="\n")

collection = client.get_or_create_collection("courses")

embed_data(collection)

print("Remade")
print(collection)
print(collection.count(), end="\n")