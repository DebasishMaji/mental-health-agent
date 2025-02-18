from typing import List

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory, ConversationBufferMemory


class MemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(return_messages=True)

    def save_conversation(self, user_input: str, ai_response: str):
        self.memory.save_context(
            {"input": user_input},
            {"output": ai_response}
        )

    def get_history(self) -> List[str]:
        return self.memory.load_memory_variables({})["history"]
