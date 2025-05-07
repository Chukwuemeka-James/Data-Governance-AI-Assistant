from utils import load_pdf_file, text_split, download_hugging_face_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os
import time

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

extracted_data = load_pdf_file(data='Knowledge_Source/')
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "datagovbot"

# Try to create the index, handling the case where it already exists
try:
    print(f"Creating index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws", 
            region="us-east-1"
        ) 
    )
    # Wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)
    print("Index created and ready.")
except Exception as e:
    if "already exists" in str(e):
        print(f"Index '{index_name}' already exists. Proceeding with upsert...")
    else:
        raise e

# Upsert the embeddings into your Pinecone index
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings,
)