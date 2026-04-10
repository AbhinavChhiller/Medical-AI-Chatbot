
from flask import Flask, render_template, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from src.prompt import *
from google import genai
import os


app = Flask(__name__)


load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


embeddings = download_hugging_face_embeddings()

index_name = "medical-chatbot" 
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)




retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})
client = genai.Client()



@app.route("/")
def index():
    return render_template('chat.html')



@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    print(msg)

    docs = retriever.get_relevant_documents(msg)
    doc_text = "\n\n".join([doc.page_content for doc in docs])

    prompt_text = f"{system_prompt}\n\nRelevant documents:\n{doc_text}\n\nUser: {msg}\nAssistant:"

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt_text,
    )

    answer = response.text
    print("Response:", answer)
    return answer



if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)