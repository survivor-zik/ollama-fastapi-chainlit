from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import AutoTokenizer
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# tokenizer = AutoTokenizer.from_pretrained("./model/llm/gemma-7b-it.Q5_K_M-v2.gguf", model_kwargs={'device': 'cuda'})
tokenizer = AutoTokenizer.from_pretrained("google/gemma-7b-it", token=os.getenv('ACCESS_TOKEN'),
                                          # cache_folder='./model/llm/',
                                          model_kwargs={'device': 'cuda'})


def return_splitter(max_tokens: int, prompt):
    return RecursiveCharacterTextSplitter.from_huggingface_tokenizer(tokenizer=tokenizer, chunk_size=max(
        max_tokens - (tokens_len(prompt) + 1000), 1000), chunk_overlap=200, separators=["\n\n"],
                                                                     is_separator_regex=False)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def tokens_len(text: str):
    tokens = tokenizer.encode(text=text)
    return len(tokens)


def get_vector_store(collection: str):
    """
    This function returns the vector store object.
    Parameters
    ----------

    Returns
    -------
    vec_store : object, which is the vector store object.
    """
    vec_store = Chroma(
        collection,
        persist_directory="./database",
        embedding_function=HuggingFaceEmbeddings(model_name="WhereIsAI/UAE-Large-V1",
                                                 cache_folder='./model/embedding_model/',
                                                 model_kwargs={'device': 'cuda'}),
    )
    return vec_store


def stringify_searched_docs(docs):
    docs_str = ""
    for doc in docs:
        docs_str += f"\n{doc.page_content} \n"
        # docs_str += f"{str(doc.metadata)}"
    return docs_str
