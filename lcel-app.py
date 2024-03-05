import chainlit as cl
from src.chatbot import Chatbot
from src.data_parse import read_pdf_chain


@cl.on_chat_start
async def on_message():
    chat = Chatbot()
    cl.user_session.set("llm", chat.lcel)
    cl.user_session.set("chat", chat)
    elements = [
        cl.Image(name="ByteCorp", display="inline", path="./OIP.jpeg")
    ]
    await cl.Message(content="Hello there", elements=elements).send()
    files = None

    # Wait for the user to upload a PDF file
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a PDF file to begin!",
            accept=["application/pdf"],
            max_size_mb=50,
            timeout=180,
        ).send()
    file = files[0]
    text_file = file

    read_pdf_chain(text_file, file.name)

    msg = cl.Message(content=f"Processed `{file.name}`")
    await msg.send()


@cl.on_message
async def on_message(message: cl.Message):
    llm = cl.user_session.get("llm")
    chat = cl.user_session.get("chat")
    mess = cl.Message(content="")
    print(message.content)
    context = await cl.make_async(chat.get_ordered_docs)(input_query=message.content)
    response = await llm.ainvoke({
        "question": message.content,
        "context": context,
        "chat_history": await cl.make_async(chat.memory.load_memory_variables)('chat_history')
    })

    await cl.Message(content=response).send()
    chat.memory.save_context({'input': message.content}, {'output': response})
