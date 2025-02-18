from typing import TypedDict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from agent.memory import MemoryManager


class AgentState(TypedDict):
    user_input: str
    history: List[str]
    response: str
    needs_escalation: bool


class MentalHealthAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)
        self.memory = MemoryManager()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("process_input", self.process_input)
        workflow.add_node("assess_risk", self.assess_risk)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("escalate", self.escalate)

        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "assess_risk")

        workflow.add_conditional_edges(
            "assess_risk",
            self.decide_escalation,
            {"escalate": "escalate", "continue": "generate_response"}
        )

        workflow.add_edge("generate_response", END)
        workflow.add_edge("escalate", END)

        return workflow.compile()

    def process_input(self, state: AgentState):
        return {"history": self.memory.get_history()}

    def assess_risk(self, state: AgentState):
        risk_keywords = {"suicide", "kill myself", "end it all"}
        input_text = state["user_input"].lower()
        return {
            "needs_escalation": any(kw in input_text for kw in risk_keywords)
        }

    def decide_escalation(self, state: AgentState):
        return "escalate" if state["needs_escalation"] else "continue"

    def generate_response(self, state: AgentState):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You're a compassionate mental health assistant. Use conversation history to provide personalized support."),
            ("human", "{user_input}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "user_input": state["user_input"],
            "history": "\n".join(str(msg) for msg in state["history"])
        })

        self.memory.save_conversation(state["user_input"], response.content)
        return {"response": response.content}

    def escalate(self, state: AgentState):
        self.memory.save_conversation(state["user_input"], "[CRISIS ESCALATED]")
        return {"response": "🆘 Connecting you to a human counselor immediately..."}