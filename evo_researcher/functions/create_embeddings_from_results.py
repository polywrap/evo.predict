try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    print("pysqlite3-binary not found, using sqlite3 instead.")


import os
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from evo_researcher.models.WebScrapeResult import WebScrapeResult
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic.types import SecretStr
from evo_researcher.utils.secrets import secret_str_from_env
from prediction_market_agent_tooling.gtypes import secretstr_to_v1_secretstr


def create_embeddings_from_results(results: list[WebScrapeResult], text_splitter: RecursiveCharacterTextSplitter, api_key: SecretStr | None = None) -> Chroma:
    if api_key == None:
        api_key = secret_str_from_env("OPENAI_API_KEY")
    
    collection = Chroma(embedding_function=OpenAIEmbeddings(api_key=secretstr_to_v1_secretstr(api_key)))
    texts = []
    metadatas = []

    for scrape_result in results:
        text_splits = text_splitter.split_text(scrape_result.content)
        texts += text_splits
        metadatas += [scrape_result.dict() for _ in text_splits]

    collection.add_texts(
        texts=texts,
        metadatas=metadatas
    )
    return collection
