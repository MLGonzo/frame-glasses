from typing import TypedDict, Annotated, Optional, List, Literal
from langgraph.graph import add_messages, StateGraph, END, START, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os
from frame_msg import FrameMsg, TxCaptureSettings, RxPhoto
from datetime import datetime
import base64
from openai import OpenAI
from PIL import Image
import io
import asyncio
import time
from utils.camera_utils import capture_photo
import requests
from typing import Dict, Any

load_dotenv()

# Global frame object
frame: Optional[FrameMsg] = None

def set_frame(frame_obj: FrameMsg):
    """Set the global frame object."""
    global frame
    frame = frame_obj

class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]
    last_photo_path: Optional[str]

@tool
def get_weather(location: str) -> str:
    """Get current weather information for a location.
    Args:
        location: City name or location to get weather for
    Returns:
        str: Weather information including temperature, conditions, and humidity
    """
    try:
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            return "Weather API key not configured. Please set OPENWEATHER_API_KEY in .env file."
            
        # Make API request to OpenWeatherMap
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'  # Use metric units
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        
        # Format the weather information
        weather_info = (
            f"Current weather in {location}:\n"
            f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"Conditions: {description}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except Exception as e:
        return f"Error processing weather data: {str(e)}"

def take_photo() -> str:
    """Take a photo using the Frame camera. Use this when you need to see what's in front of the user.
    Returns the path to the taken photo."""
    try:
        if not frame:
            raise Exception("No frame available for taking photos")
            
        # Create photos directory if it doesn't exist
        os.makedirs('photos', exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        photo_path = os.path.join('photos', f'frame_photo_{timestamp}.jpg')
        
        # Capture the photo using camera_utils
        image = asyncio.run(capture_photo(frame))
        
        # Save the image
        image.save(photo_path)
        
        return photo_path
    except Exception as e:
        print(f"Error taking photo: {e}")
        raise

def _setup_chatbot():
    """Set up and return the chatbot graph."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ['OPENAI_API_KEY']
    )
    vision_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    def chatbot(state: BasicChatState):
        """Get response from the AI chatbot."""
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    def should_take_photo(state: BasicChatState) -> Literal["take_photo", "end"]:
        """Use LLM to determine if we need to take a photo based on the last human message."""
        decision_prompt = """You are a decision maker for a camera system in smart glasses. Based on the user's last message, determine if a photo should be taken.
        Since you're in smart glasses, any request for visual information, understanding surroundings, or seeing what's in front of the user should trigger a photo.
        This includes requests like "what's in front of me", "what do you see", or any question about the user's environment.
        Respond with exactly one word: 'yes' if a photo should be taken, or 'no' if not.
        
        User's last message:
        {last_message}
        
        Decision:"""
        
        # Get the last human message
        last_human_message = next((msg.content for msg in reversed(state["messages"]) 
                                 if isinstance(msg, HumanMessage)), "")
        
        # Get decision from LLM
        response = llm.invoke(decision_prompt.format(last_message=last_human_message))
        decision = response.content.strip().lower()
        return "take_photo" if decision == "yes" else "end"

    def should_get_weather(state: BasicChatState) -> Literal["get_weather", "take_photo", "end"]:
        """Use LLM to determine if we need to get weather information based on the last human message."""
        decision_prompt = """You are a decision maker for a weather information system. Based on the user's last message, determine if weather information should be fetched.
        If the message asks about weather, temperature, or conditions in any location, respond with 'weather'.
        If the message asks about visual information or what's in front of the user, respond with 'photo'.
        Otherwise, respond with 'end'.
        
        User's last message:
        {last_message}
        
        Decision:"""
        
        # Get the last human message
        last_human_message = next((msg.content for msg in reversed(state["messages"]) 
                                 if isinstance(msg, HumanMessage)), "")
        
        # Get decision from LLM
        response = llm.invoke(decision_prompt.format(last_message=last_human_message))
        decision = response.content.strip().lower()
        
        if decision == "weather":
            return "get_weather"
        elif decision == "photo":
            return "take_photo"
        return "end"

    def get_weather_node(state: BasicChatState):
        """Node that handles getting weather information."""
        # Extract location from the last message
        last_message = next((msg.content for msg in reversed(state["messages"]) 
                           if isinstance(msg, HumanMessage)), "")
        
        # Use LLM to extract location from the message
        location_prompt = f"""Extract the location from this message. If no specific location is mentioned, return 'London' as default.
        Message: {last_message}
        Location:"""
        
        location_response = llm.invoke(location_prompt)
        location = location_response.content.strip()
        
        # Get weather information
        weather_info = get_weather(location)
        
        return {
            "messages": [AIMessage(content=weather_info)]
        }

    def take_photo_node(state: BasicChatState):
        """Node that handles taking a photo."""
        photo_path = take_photo()
        # Update the state with the new photo path
        state["last_photo_path"] = photo_path
        return {
            "messages": [AIMessage(content=f"Photo taken and saved to {photo_path}")],
            "last_photo_path": photo_path
        }

    def analyze_photo(state: BasicChatState):
        """Analyze the photo using vision."""
        print(state)
        if not state.get("last_photo_path"):
            return {
                "messages": [AIMessage(content="No image available for analysis.")]
            }
            
        try:
            # Encode the image
            with open(state["last_photo_path"], "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Get the original query
            original_query = state["messages"][-1].content
            
            # Create the vision request
            response = vision_client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "input_text", "text": original_query },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ],
            )
            
            return {
                "messages": [AIMessage(content=response.output_text)]
            }
            
        except Exception as e:
            return {
                "messages": [AIMessage(content=f"Error analyzing image: {str(e)}")]
            }

    # Create the graph
    graph = StateGraph(BasicChatState)
    
    # Add nodes
    graph.add_node("chatbot", chatbot)
    graph.add_node("take_photo", take_photo_node)
    graph.add_node("analyze_photo", analyze_photo)
    graph.add_node("get_weather", get_weather_node)
    
    # Set entry point
    graph.set_entry_point("chatbot")
    
    # Add edges
    graph.add_conditional_edges(
        "chatbot",
        should_get_weather,
        {
            "get_weather": "get_weather",
            "take_photo": "take_photo",
            "end": END
        }
    )
    graph.add_edge("take_photo", "analyze_photo")
    graph.add_edge("analyze_photo", END)
    graph.add_edge("get_weather", END)
    
    return graph.compile()

# Initialize the chatbot once
chatbot_app = _setup_chatbot()

# Store conversation history
conversation_history = []

async def get_ai_response(text: str, frame_obj: Optional[FrameMsg] = None, last_photo_path: Optional[str] = None) -> tuple[str, bool]:
    """
    Get a response from the AI chatbot for the given text, maintaining conversation history.
    
    Args:
        text: The input text to get a response for
        frame_obj: Optional FrameMsg instance for photo taking
        last_photo_path: Optional path to the last taken photo
        
    Returns:
        tuple[str, bool]: The AI's response text and whether a photo should be taken
        
    Raises:
        Exception: If there's an error getting the response
    """
    try:
        # Set the global frame if provided
        if frame_obj:
            set_frame(frame_obj)
            
        # Add the user's message to history
        conversation_history.append(HumanMessage(content=text))
        
        # Get response using full conversation history
        result = chatbot_app.invoke({
            "messages": conversation_history,
            "last_photo_path": last_photo_path
        })
        
        # Extract the response text
        if result and "messages" in result and len(result["messages"]) > 0:
            ai_message = result["messages"][-1]
            conversation_history.append(ai_message)
            return ai_message.content, False
            
        else:
            raise Exception("No response received from AI")
            
    except Exception as e:
        print(f"Error getting AI response: {e}")
        raise

def clear_conversation_history():
    """Clear the conversation history."""
    global conversation_history
    conversation_history = []