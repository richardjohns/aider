from typing import Optional
import chromadb
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain

from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET
from loguru import logger

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

def extract_urls_from_sitemap(sitemap):
    """
    Extract all URLs from a sitemap XML string.

    Args:
        sitemap_string (str): The sitemap XML string.

    Returns:
        A list of URLs extracted from the sitemap.
    """
    # Parse the XML from the string
    root = ET.fromstring(sitemap)

    # Define the namespace for the sitemap XML
    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Find all <loc> elements under the <url> elements
    urls = [
        url.find("ns:loc", namespace).text for url in root.findall("ns:url", namespace)
    ]

    # Return the list of URLs
    return urls


class KnowledgeBase:
    def __init__(
        self,
        sitemap_url: str,
        chunk_size: int,
        chunk_overlap: int,
        pattern: Optional[str] = None,
    ):
        logger.info("Building the knowledge base ...")

        logger.info("Loading sitemap from {sitemap_url} ...", sitemap_url=sitemap_url)
        sitemap = requests.get(sitemap_url).text
        urls = extract_urls_from_sitemap(sitemap)

        if pattern:
            logger.info("Filtering URLs with pattern {pattern} ...", pattern=pattern)
            urls = [x for x in urls if pattern in x]
        logger.info("{n} URLs extracted", n=len(urls))

        logger.info("Loading URLs content ...")
        loader = UnstructuredURLLoader(urls)
        data = loader.load()

        logger.info("Splitting documents in chunks ...")
        doc_splitter = CharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        docs = doc_splitter.split_documents(data)
        
        logger.info("{n} chunks created", n=len(docs))

        logger.info("Building the vector database ...")
        persist_directory = 'db'
        collection_name = 'NextJS'
        embeddings = OpenAIEmbeddings()
        ids = [str(i) for i in range(len(docs))]

        embeddings = OpenAIEmbeddings()
        if os.path.exists(persist_directory):
            logger.info("Loading existing vector database ...")
            self.vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            logger.info("Creating new vector database ...")
            self.vectordb = Chroma.from_documents(docs, embeddings, ids, collection_name, persist_directory)

        logger.info("Building the retrieval chain ...")
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(),
            chain_type="map_reduce",
            retriever=self.vectordb.as_retriever(),
        )

        logger.info("Knowledge base created!")

    def get_vectordb(self):
        "Get the vectordb"
        return self.vectordb

    def peek(self):
        "Get the first 10 items in the collection"
        return self.vectordb.peek(10)

    def ask(self, query: str):
        logger.info(f"Received question: {query}")
        if not query.strip():
            logger.error("Error: The query is empty.")
            return "Error: The query is empty. Please provide a valid question."
        try:
            response = self.chain({"question": query}, return_only_outputs=True)
            logger.info(f"Response generated for the question: {query}")
            return response
        except IndexError:
            logger.error(f"No relevant documents found for the question: {query}")
            return "No relevant documents found for your question. Please try another question."
        except Exception as e:
            logger.error(f"Error while generating response for the question: {query}. Error: {str(e)}")
            return f"Error: An error occurred while processing the question. Error: {str(e)}"

    @classmethod
    def load(cls, chroma_db_file: str):
        """
        Load a KnowledgeBase instance from a saved Chroma database file.

        Args:
            chroma_db_file (str): The path to the saved Chroma database file.

        Returns:
            A KnowledgeBase instance.
        """
        # Create an instance of the OpenAIEmbeddings class
        embeddings = OpenAIEmbeddings()

        # Extract the directory from the chroma_db_file path
        chroma_db_dir = os.path.dirname(chroma_db_file)

        # Create an instance of the Chroma class
        vectordb = Chroma(persist_directory=chroma_db_dir, embedding_function=embeddings)

        # Create a new KnowledgeBase instance
        kb = cls.__new__(cls)

        # Set the vectordb attribute
        kb.vectordb = vectordb

        # Set the retrieval chain
        kb.chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(),
            chain_type="map_reduce",
            retriever=vectordb.as_retriever(),
        )

        return kb


if __name__ == "__main__":
    # Build the knowledge base
    kb = KnowledgeBase(
        sitemap_url="https://nextjs.org/sitemap.xml",
        pattern="docs/getting-started/",
        chunk_size=8000,
        chunk_overlap=3000,
    )
