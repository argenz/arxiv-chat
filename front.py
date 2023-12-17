import streamlit as st
from arxivapi import ArxivAPI
from qdrantapi import QdrantAPI
from vertexapi import VertexAPI
from dotenv import load_dotenv
from prompts import prompt_completion
import logging as log
import os


load_dotenv()

log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


current_dir = os.getcwd()

# intialize vertex AI SDK and arxiv API
vertex_api = VertexAPI()
arxiv_api = ArxivAPI()
qdrant_client = QdrantAPI()

# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#     "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chat over the latest papers in cs.IR on Arxiv.")
st.caption("🚀 A streamlit chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi, I'm a chatbot that has access to all abstracts of Arxiv Papers submitted since Feb 2023 in the subject field of Information Retrieval (cs.IR). What would you like to explore?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    # semantic search and get most relevant paragraphs
    hits = qdrant_client.query_index(collection_name='information_retrieval', query=prompt, k = 20)

    # RAG format context
    context = []
    for hit in hits: 
        payload = hit.payload 
        context.append(f'Paragraph: {payload["summary"]} - Metadata: {dict((k, payload[k]) for k in ("authors", "link", "published", "title"))}')

    context = '\n\n'.join(context)
    formatted_prompt = prompt_completion.format(user_question=prompt, context=context)

    # get completion
    log.info(f"Requesting completion for the following formatted prompt: {formatted_prompt}.")
    msg = vertex_api.get_completion(formatted_prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)