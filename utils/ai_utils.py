from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]

def _setup_chatbot():
    """Set up and return the chatbot graph."""
    llm = ChatOpenAI(model="gpt-4", api_key=os.environ['OPENAI_API_KEY'])

    def chatbot(state: BasicChatState):
        return {
            "messages": [llm.invoke(state["messages"])]
        }

    graph = StateGraph(BasicChatState)
    graph.add_node("chatbot", chatbot)
    graph.set_entry_point("chatbot")
    graph.add_edge("chatbot", END)
    
    return graph.compile()

# Initialize the chatbot once
chatbot_app = _setup_chatbot()

# Store conversation history
conversation_history = []

async def get_ai_response(text: str) -> str:
    """
    Get a response from the AI chatbot for the given text, maintaining conversation history.
    
    Args:
        text: The input text to get a response for
        
    Returns:
        str: The AI's response text
        
    Raises:
        Exception: If there's an error getting the response
    """
    try:
        # Add the user's message to history
        conversation_history.append(HumanMessage(content=text))
        
        # Get response using full conversation history
        result = chatbot_app.invoke({
            "messages": conversation_history
        })
        
        # Extract the response text from the result
        if result and "messages" in result and len(result["messages"]) > 0:
            ai_message = result["messages"][-1]
            # Add AI's response to history
            conversation_history.append(ai_message)
            return ai_message.content
        else:
            raise Exception("No response received from AI")
            
    except Exception as e:
        print(f"Error getting AI response: {e}")
        raise

def clear_conversation_history():
    """Clear the conversation history."""
    global conversation_history
    conversation_history = []