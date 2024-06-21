import os
import sys

import openai
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
# from langchain_community.document_loaders import DirectoryLoader # DirectoryLoader
from langchain_community.document_loaders import TextLoader # TextLoader
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain # RetrievalQA
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper

from constants import constants

print('APIKEY', constants.APIKEY)

# import constants
# sys.path.insert(0, '/constants/')
os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = TextLoader("src/data/data.txt") # Use this line if you only need data.txt
  # loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    # index = VectorstoreIndexCreator().from_loaders([loader])
    index = VectorstoreIndexCreator(embedding=OpenAIEmbeddings()).from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  # print(constants.APIKEY)

  result = chain({"question": query, "chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None