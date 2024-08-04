"""
    Streamlit version, using LangChain, according to IBM technology tutorial:
    https://www.youtube.com/watch?v=XctooiH0moI
    and blog tutorial:
    https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/
"""
import streamlit as st
import os

# from langchain.document_loaders import PyPDFLoader
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.chains import RetrievalQA
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter

#from wxai_langchain.llm import LangChainInterface
import replicate

llm = {
    'model':'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5',
    'decoding_method':'sample',
    'max_length':200,
    'temperature':0.5,
    'top_p':0.9,
    }


def clear_chat_history() -> None:
    """ Clear chat history (usually on button click)
    """
    st.session_state.messages = [{"role": "assistant", "content": "What would you like to know about your publications?"}]
    return None


def generate_llama2_response(prompt_input):
    """ Generate LLaMA2 response.
    """
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(llm['model'], 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":llm['temperature'], "top_p":llm['top_p'],
                                  "max_length":llm['max_length'], "repetition_penalty":1})
    return output


# Main title
st.set_page_config(page_title="PubRAG Query 🔍")
st.title('PubRAG Query 📚🔍')

# # Sidebar
# with st.sidebar:
#     st.title('PubRAG 📚')
#     if 'api' in llm:
#         st.success('API token provided', icon='✅')
#         llm['api'] = st.secrets['REPLICATE_API_TOKEN']
#     else:
#         llm['api'] = st.text_input('Enter [Replicate](https://replicate.com/account/api-tokens) API token:', type='password')
#         if not (llm['api'].startswith('r8_') and len(llm['api'])==40):
#             st.warning('API token required', icon='⚠️')
#         else:
#             st.success('API token provided', icon='✅')
#     os.environ['REPLICATE_API_TOKEN'] = llm['api']

#     st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# # Store LLM generated responses
# if ("messages" not in st.session_state) and ('api' in llm):
#     st.session_state.messages = [{"role": "assistant", "content": "What would you like to know about your publications?"}]

# # Display or clear chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# # User-provided prompt
# if prompt := st.chat_input(disabled=not llm['api']):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.write(prompt)

# # Generate a new response if last message is not from assistant
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             response = generate_llama2_response(prompt)
#             placeholder = st.empty()
#             full_response = ''
#             for item in response:
#                 full_response += item
#                 placeholder.markdown(full_response)
#             placeholder.markdown(full_response)
#     message = {"role": "assistant", "content": full_response}
#     st.session_state.messages.append(message)

