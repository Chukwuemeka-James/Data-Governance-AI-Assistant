import modal
from modal import App
from app import app as flask_app
import os

# Define the Modal App
app = modal.App("niftybot-api")

# Create the Modal Image with all required packages and explicitly add local modules
image = modal.Image.debian_slim().pip_install(
    "flask",
    "langchain",
    "langchain-groq",
    "langchain-pinecone",
    "python-dotenv",
    "pinecone-client[grpc]",
    "pypdf",
    "huggingface_hub",
    "sentence-transformers>=2.2.2",
    "langchain-community",
    "langchain-experimental",
    "ipykernel",
    "flask-cors"
).add_local_python_source("app", "DataGotBot")  # Explicitly add local modules

if os.path.exists("templates"):
    image = image.add_local_dir("templates", "/root/templates")
if os.path.exists("static"):
    image = image.add_local_dir("static", "/root/static")

# Define the web endpoint
@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("PINECONE_API_KEY"),
        modal.Secret.from_name("groq_api_key")
    ]
)
@modal.wsgi_app()  # This replaces web_server for Flask apps
def flask_app_endpoint():
    return flask_app