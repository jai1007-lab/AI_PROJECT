from typing import List, Dict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger
import os

logger = setup_logger(__name__)

# Helper Function to Transform Quiz Output
def transform_json_dict(input_data: dict) -> dict:
    """Transform the quiz question response dictionary."""
    quiz_question = QuizQuestion(**input_data)
    transformed_choices = {choice.key: choice.value for choice in quiz_question.choices}
    
    transformed_data = {
        "question": quiz_question.question,
        "choices": transformed_choices,
        "answer": quiz_question.answer,
        "explanation": quiz_question.explanation
    }
    return transformed_data

# Add the missing read_text_file function
def read_text_file(file_path: str) -> str:
    """
    Read and return the contents of a text file.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return ""
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

# Placeholder classes for pydantic validation
from langchain_core.pydantic_v1 import BaseModel, Field

class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")

class RAGRunnable:
    def __init__(self, func):
        self.func = func
    
    def __or__(self, other):
        def chained_func(*args, **kwargs):
            return other(self.func(*args, **kwargs))
        return RAGRunnable(chained_func)
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

# RAGpipeline for Direct Text Input
class RAGpipeline:
    def __init__(self, splitter=None, vectorstore_class=None, embedding_model=None, verbose=False):
        """
        Initialize the RAG pipeline with optional configurations.
        """
        default_config = {
            "splitter": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            "vectorstore_class": Chroma,
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001')
        }
        self.splitter = splitter or default_config["splitter"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.verbose = verbose

    def load_text(self, text: str) -> List[Document]:
        """
        Load transcribed text directly as a Document object.
        """
        document = Document(page_content=text, metadata={"source": "transcription"})
        return [document]

    def split_loaded_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for processing.
        """
        if self.verbose:
            logger.info(f"Splitting {len(documents)} documents")
            
        chunks = self.splitter.split_documents(documents)
        
        if self.verbose:
            logger.info(f"Split documents into {len(chunks)} chunks")
        
        return chunks

    def create_vectorstore(self, documents: List[Document]):
        """
        Create a vectorstore from the documents.
        """
        if self.verbose:
            logger.info(f"Creating vectorstore from {len(documents)} documents")
        
        self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)

        if self.verbose:
            logger.info(f"Vectorstore created")
        
        return self.vectorstore

    def compile(self):
        """
        Compile the RAG pipeline for processing.
        """
        self.load_text = RAGRunnable(self.load_text)
        self.split_loaded_documents = RAGRunnable(self.split_loaded_documents)
        self.create_vectorstore = RAGRunnable(self.create_vectorstore)

        if self.verbose:
            logger.info(f"Pipeline compiled")

    def __call__(self, text: str):
        """
        Execute the RAG pipeline with direct text input.
        """
        if self.verbose:
            logger.info(f"Executing RAG pipeline with direct text input")

        documents = self.load_text(text)
        chunks = self.split_loaded_documents(documents)
        vectorstore = self.create_vectorstore(chunks)

        if self.verbose:
            logger.info(f"RAG pipeline completed")

        return vectorstore

# QuizBuilder for Direct Text Input
class QuizBuilder:
    def __init__(self, vectorstore, topic, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=QuizQuestion),
            "prompt": read_text_file("prompt/quizzify-prompt.txt")
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        
        self.vectorstore = vectorstore
        self.topic = topic  # Use the transcribed text as the topic
        self.verbose = verbose

        if vectorstore is None:
            raise ValueError("Vectorstore must be provided")
        if topic is None:
            raise ValueError("Topic must be provided")
    
    def compile(self):
        """Compile the chain for generating quiz questions."""
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["topic"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        retriever = self.vectorstore.as_retriever()
        
        runner = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        
        chain = runner | prompt | self.model | self.parser
        
        if self.verbose:
            logger.info(f"Chain compilation complete")
        
        return chain

    def create_questions(self, num_questions: int = 5) -> List[Dict]:
        """Create quiz questions from the transcribed text."""
        if self.verbose:
            logger.info(f"Creating {num_questions} questions")
        
        chain = self.compile()
        generated_questions = []

        for _ in range(num_questions):
            response = chain.invoke(self.topic)
            response = transform_json_dict(response)

            if self.validate_response(response):
                response["choices"] = self.format_choices(response["choices"])
                generated_questions.append(response)
                
                if self.verbose:
                    logger.info(f"Valid question added: {response}")
            else:
                if self.verbose:
                    logger.warning(f"Invalid response format")

        return generated_questions
