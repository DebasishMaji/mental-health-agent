from agent.workflow import MentalHealthAgent

from dotenv import load_dotenv
load_dotenv()  # Loads OPENAI_API_KEY from .env file


class MentalHealthChat:
    def __init__(self):
        self.agent = MentalHealthAgent()

    def chat(self):
        print("Mental Health Assistant: Hello. How can I support you today? (Type 'exit' to quit)")
        while True:
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Assistant: Take care of yourself. Reach out anytime.")
                break

            result = self.agent.workflow.invoke({
                "user_input": user_input,
                "history": [],
                "response": "",
                "needs_escalation": False
            })

            if "response" in result:
                print(f"Assistant: {result['response']}")
            else:
                print("Assistant: I'm here to listen. Could you tell me more about that?")


if __name__ == "__main__":
    MentalHealthChat().chat()


