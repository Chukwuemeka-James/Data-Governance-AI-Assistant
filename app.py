from flask import Flask, render_template, jsonify, request
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import re

from DataGotBot.prompt import *
from DataGotBot.utils import download_hugging_face_embeddings

import os

app = Flask(__name__)

load_dotenv()

import os
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
groq_api_key = os.getenv("groq_api_key")


embeddings = download_hugging_face_embeddings()


index_name = "datagovbot"

# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})


llm=ChatGroq(groq_api_key=groq_api_key,model_name="deepseek-r1-distill-llama-70b",temperature=0.3)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


@app.route("/")
def index():
    return render_template('DataGovBot.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    response = rag_chain.invoke({"input": msg})
    clean_response = re.sub(r"<think>.*?</think>", "", response['answer'], flags=re.DOTALL).strip()
    print("Response : ", response["answer"])
    return str(clean_response)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)