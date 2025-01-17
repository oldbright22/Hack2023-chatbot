
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub

from langchain.vectorstores import Pinecone

from langchain.chains import LLMChain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from dotenv import find_dotenv, load_dotenv
from getpass import getpass

import streamlit as st
import pinecone


HUGGINGFACE_API_TOKEN = st.secrets["HUGGINGFACE_API_TOKEN"]
os.environ["HUGGINGFACE_API_TOKEN"] = HUGGINGFACE_API_TOKEN   

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = 
PINECONE_ENV = 
PINECONE_INDEX = 


class MaverickChatbot:
    
    def __init__(self):
        load_dotenv(find_dotenv())
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    def get_db_maverick(_self):
        pinecone.init(
            api_key=PINECONE_API_KEY, 
            environment=PINECONE_ENV  
        )

        index_name=PINECONE_INDEX

        db = Pinecone.from_existing_index(index_name, _self.embeddings)

        return db

    @st.cache_data(show_spinner=False)
    def get_response_from_query(_self, _db, query, k=4):
        """
        Function that generates a response to a customer question using the gpt-3.5-model and the docs provided
        """

        docs = _db.similarity_search(query, k=k)
        docs_page_content = " ".join([d.page_content for d in docs])

        #chat = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

        repo_id = "tiiuae/falcon-7b-instruct"
        chat = HuggingFaceHub(huggingfacehub_api_token=HUGGINGFACE_API_TOKEN, 
                            repo_id=repo_id, 
                            model_kwargs={"temperature":0.7, "max_new_tokens":200})


        # Template to use for the system message prompt
        template = """
        You are a helpful assistant named Kamal that can answer customer questions related to an e-commerce platform that sells retail products or services.
  
        You also act as a polite chatbot, responding to user phrases like "Hello", "Hi", "Sure!", etc.

        Type a small appreciation message to the customer after using your services, when customer says phrases like "Thank you", "That's all", "Nothing more at this time", etc.
        
        If the input provided by the customer seems incomplete, you Kamal will not add supplementing words in the response.

        Reply to customer input, with customer name if provided. Example: Sure Mike! ...

        First, you classify the sentiment of the customer's question or statement and use only the information provided previously to answer the question, taking into account the customer's sentiment.

        If you do not have enough information or couldn't find information to answer the question, respond with "I'm sorry, and request more information."

        If the input is not a question, you act as a chatbot assisting customers.

        Your responses should be brief but contain enough detail.
        """
        

        # Template to use for the system message prompt
        #template = """
        #    You are an assistant designed to answer customer inquiries of an e-commerce platform that sells retail products {docs}.
        #    You are able to respond politely and accordingly to user phrases like "Thank you", "Hello", etc.
        #    You will classify the sentiment of the customer's question or statement.
        #    You will use only the given information to answer the question, considering the sentiment of the customer's input.
        #    If you lack the necessary information or can't find a suitable answer, You will respond with I'm sorry, can you provide more information.
        #    If the customer's input is not a question, you will act as a chatbot assisting customers and respond to user phrases like "Thank you", "Hello", etc politely and accordingly.
        #    Your responses should be short but contain enough details.
        #    """
        
        
        #template = """
        #You are a helpful AI assistant, that provides answers for questions asked politely related to ecommerce retail products or services {docs}.
        #Your name is Kamal.

        #[Kamal]: I'm here to assist you with any questions or concerns you may have about our retail products and services.

        #[Kamal]: Please feel free to ask me about:

        #1. Product information and specifications
        #2. Assistance with returns and exchanges
        #4. Payment and billing inquiries
        #5. Recommendations based on your preferences
        #6. Any other assistance you may require

        #[Kamal]: Your satisfaction is our priority, and I'm here to make your shopping experience as smooth as possible. If you're ready, go ahead and ask me anything!

        #[Kamal]: To get started, simply type your question or request, and I'll do my best to assist you promptly.

        #[Kamal]: If you ever want to exit the conversation, just type "Exit" or "Goodbye," and I'll be here whenever you need help again.

        #[Kamal]: Let's get started! How can I assist you today?
        #"""


        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # Human question prompt
        human_template = "Respond to the customer inquiry : {question}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
     
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chain = LLMChain(llm=chat, prompt=chat_prompt)

        try:
            response = chain.run(question=query, docs=docs_page_content)

            return response
        except:
            return None
