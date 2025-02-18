from typing import TypedDict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from agent.memory import MemoryManager


# class AgentState(TypedDict):
#     user_input: str
#     history: List[str]
#     response: str
#     needs_escalation: bool
#
#
# class MentalHealthAgent:
#     def __init__(self):
#         self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)
#         self.memory = MemoryManager()
#         self.workflow = self._build_workflow()
#
#     def _build_workflow(self):
#         workflow = StateGraph(AgentState)
#
#         workflow.add_node("process_input", self.process_input)
#         workflow.add_node("assess_risk", self.assess_risk)
#         workflow.add_node("generate_response", self.generate_response)
#         workflow.add_node("escalate", self.escalate)
#
#         workflow.set_entry_point("process_input")
#         workflow.add_edge("process_input", "assess_risk")
#
#         workflow.add_conditional_edges(
#             "assess_risk",
#             self.decide_escalation,
#             {"escalate": "escalate", "continue": "generate_response"}
#         )
#
#         workflow.add_edge("generate_response", END)
#         workflow.add_edge("escalate", END)
#
#         return workflow.compile()
#
#     def process_input(self, state: AgentState):
#         return {"history": self.memory.get_history()}
#
#     def assess_risk(self, state: AgentState):
#         risk_keywords = {"suicide", "kill myself", "end it all"}
#         input_text = state["user_input"].lower()
#         return {
#             "needs_escalation": any(kw in input_text for kw in risk_keywords)
#         }
#
#     def decide_escalation(self, state: AgentState):
#         return "escalate" if state["needs_escalation"] else "continue"
#
#     def generate_response(self, state: AgentState):
#         prompt = ChatPromptTemplate.from_messages([
#             ("system",
#              "You're a compassionate mental health assistant. Use conversation history to provide personalized support."),
#             ("human", "{user_input}")
#         ])
#
#         chain = prompt | self.llm
#         response = chain.invoke({
#             "user_input": state["user_input"],
#             "history": "\n".join(str(msg) for msg in state["history"])
#         })
#
#         self.memory.save_conversation(state["user_input"], response.content)
#         return {"response": response.content}
#
#     def escalate(self, state: AgentState):
#         self.memory.save_conversation(state["user_input"], "[CRISIS ESCALATED]")
#         return {"response": "🆘 Connecting you to a human counselor immediately..."}

from typing import TypedDict, List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from transformers import pipeline  # Added for emotional analysis


class AgentState(TypedDict):
    user_input: str
    history: List[str]
    response: str
    needs_escalation: bool
    emotional_state: str  # New state field


class MentalHealthAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.5)
        self.memory = MemoryManager()
        self.emotion_analyzer = pipeline(  # Added emotional analysis
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base"
        )
        self.workflow = self._build_enhanced_workflow()

    def _build_enhanced_workflow(self):  # Renamed for clarity
        workflow = StateGraph(AgentState)

        # Enhanced node sequence
        workflow.add_node("safety_check", self.safety_check)
        workflow.add_node("emotional_assessment", self.emotional_assessment)
        workflow.add_node("clinical_response", self.generate_clinical_response)
        workflow.add_node("escalate", self.escalate_with_resources)

        workflow.set_entry_point("safety_check")
        workflow.add_edge("safety_check", "emotional_assessment")

        workflow.add_conditional_edges(
            "emotional_assessment",
            self.determine_intervention_path,
            {"continue": "clinical_response", "escalate": "escalate"}
        )

        workflow.add_edge("clinical_response", END)
        workflow.add_edge("escalate", END)

        return workflow.compile()

    def safety_check(self, state: AgentState):
        """Added PII filtering and crisis keyword check"""
        text = state["user_input"].lower()
        crisis_keywords = {
            "suicide", "kill myself", "end it all",
            "want to die", "can't go on"
        }
        return {
            "needs_escalation": any(kw in text for kw in crisis_keywords),
            "user_input": text
        }

    def emotional_assessment(self, state: AgentState):
        """Added emotional state analysis"""
        emotion_result = self.emotion_analyzer(state["user_input"])[0]
        return {
            "emotional_state": emotion_result["label"],
            "needs_escalation": emotion_result["label"] in ["sadness", "fear"]
                                and emotion_result["score"] > 0.85
        }

    def generate_clinical_response(self, state: AgentState):
        """Enhanced therapeutic response generation"""
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """You're a mental health first responder. Follow these guidelines:
             1. Validate emotions first ("This sounds really hard")
             2. Use CBT techniques for cognitive distortions
             3. Suggest grounding exercises when anxious
             4. Maintain hopeful, non-judgmental tone

             History: {history}"""),
            MessagesPlaceholder(variable_name="conversation_history"),
            ("human", "{user_input}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "user_input": state["user_input"],
            "history": self._format_history(state["history"]),
            "conversation_history": self.memory.get_history()
        })

        # Store interaction with emotional metadata
        self.memory.save_conversation(
            state["user_input"],
            response.content
        )

        return {"response": response.content}

    def escalate_with_resources(self, state: AgentState):
        """Enhanced escalation protocol"""
        resources = [
            "Immediate connection to crisis counselor",
            "National Suicide Prevention Lifeline: 988",
            "Crisis Text Line: Text HOME to 741741"
        ]
        self.memory.save_conversation(state["user_input"], ai_response="")
        return {
            "response": "🚨 Emergency Support Activated:\n" + "\n".join(resources),
            "needs_escalation": True
        }

    # Helper methods
    def determine_intervention_path(self, state: AgentState):
        return "escalate" if state["needs_escalation"] else "continue"

    def _format_history(self, history: List[str]) -> str:
        """Convert history to therapeutic context"""
        return "\n".join(
            f"Session {i + 1}: {msg}"
            for i, msg in enumerate(history[-3:])  # Last 3 interactions
        )