from typing import List

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory, ConversationBufferMemory


class MemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(return_messages=True)
        # TODO: Add support for different memory types (e.g., long-term, short-term)
        # TODO: Implement error handling for memory operations
        # TODO: Log memory operations for auditing purposes

    def save_conversation(self, user_input: str, ai_response: str):
        self.memory.save_context(
            {"input": user_input},
            {"output": ai_response}
        )
        # TODO: Validate input and response before saving
        # TODO: Handle potential exceptions during save operation

    def get_history(self) -> List[str]:
        return self.memory.load_memory_variables({})["history"]
        # TODO: Add pagination support for large histories
        # TODO: Implement filtering options for retrieving specific conversations