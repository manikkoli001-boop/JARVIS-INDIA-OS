from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_groq import ChatGroq

# =========================
# GROQ MODEL
# =========================
llm = ChatGroq(
    groq_api_key="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",
    model_name="llama-3.1-8b-instant"
)

# =========================
# STATE
# =========================
class AgentState(TypedDict):
    message: str
    reply: str

# =========================
# NODE FUNCTION
# =========================
def think(state: AgentState):
    user_message = state["message"]
    try:
        response = llm.invoke(user_message)
        return {
            "reply": response.content
        }
    except Exception as e:
        print(f"Error invoking model: {e}")
        return {
            "reply": "I'm sorry, I couldn't understand that."
        }

# =========================
# GRAPH
# =========================
graph = StateGraph(AgentState)
graph.add_node("think", think)
graph.set_entry_point("think")
graph.add_edge("think", END)

agent = graph.compile()
