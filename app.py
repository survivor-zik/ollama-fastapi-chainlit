from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain.docstore.document import Document
import chainlit as cl
from typing import List
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from src.data_parse import read_pdf_chain
from src.chatbot import Chatbot
from src.prompt import CHAIN_PROMPT


@cl.on_chat_start
async def on_chat_start():
    # Sending an image with the local file path
    elements = [
        cl.Image(name="image1", display="inline", path="OIP.jpeg")
    ]
    files = None
    await cl.Message(content="Hello there, I am Gemma. How can I help you ?", elements=elements).send()
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a pdf file to begin!",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()

    file = files[0]
    print(file)
    read_pdf_chain(file, file.name)
    msg = cl.Message(content=f"File processed `{file.name}`...")
    await msg.send()
    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )
    chat = Chatbot()
    chain = ConversationalRetrievalChain.from_llm(
        llm=chat.llm,
        chain_type="stuff",
        retriever=chat.retreiver,
        memory=memory,
        condense_question_prompt=PromptTemplate.from_template(CHAIN_PROMPT),
        return_source_documents=True,
    )
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.ainvoke(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    await cl.Message(content=answer, elements=text_elements).send()
