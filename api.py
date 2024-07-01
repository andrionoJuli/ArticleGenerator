import logging

from fastapi import FastAPI, HTTPException
from langchain_community.chat_models import ChatOllama
from generation import ArticleGenerator
from utils import validate_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatOllama(model="llama3", format="json", temperature=1.2)

app = FastAPI()


@app.post("/generate_article/")
async def classify_texts(input_text: str):
    logger.info("Request received successfully!")
    validate_string(input_text)
    try:
        generator = ArticleGenerator(llm)
        article = generator.generate_article(input_text)
        return article
    except Exception as e:
        logger.error(f"Error during article generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
