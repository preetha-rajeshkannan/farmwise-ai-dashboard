import streamlit as st

st.set_page_config(page_title="Farmwise AI")
st.title("Farmwise AI Dashboard")
question=st.chat_input("Ask a question")

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        st.write("This is a placeholder response")