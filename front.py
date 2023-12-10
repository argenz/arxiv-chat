from openai import OpenAI
import streamlit as st
from arxivapi import ArxivAPI
from index import Index
from vertexapi import VertexAPI
from dotenv import load_dotenv
from prompts import prompt_completion
import logging as log

load_dotenv()
log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# intialize vertex AI SDK and arxiv API
vertex_api = VertexAPI()
arxiv_api = ArxivAPI()

# initialize index
index = Index(persist_dir=f'./chromadb', collection_name='information_retrieval')

# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#     "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chat over the latest papers in cs.IR on Arxiv.")
st.caption("🚀 A streamlit chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What are you interested in learning?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    
    # semantic search and get most relevant paragraphs
    result = index.query_index(query_texts=[prompt], k=20)

    # format context
    context = [f'Paragraph: {paragraph} - Link: {link}' for paragraph, link in zip(result['documents'][0], result['metadatas'][0])]
    context = '\n\n'.join(context)
    formatted_prompt = prompt_completion.format(user_question=prompt, context=context)

    # get completion
    log.info(f"Requesting completion for the following formatted prompt: {formatted_prompt}.")
    msg = vertex_api.get_completion(formatted_prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)