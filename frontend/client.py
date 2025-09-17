import os
from typing import Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv

from google import genai
from google.genai import types as genai_types

from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI

# Load env
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_PROJECT'] = "AI Nutrition Analysis"
os.environ['LANGCHAIN_TRACING_V2'] = 'true'

# Initialize memory
memory = MemorySaver()

# Langgraph state 
class CalorieState(TypedDict):
    image_bytes: Optional[bytes]
    mime: Optional[str]
    food_items: Optional[str]
    result: Optional[str]
    user_query: Optional[str]
    user_result: Optional[str]

# Tools Loader 
async def get_tools():
    try:
        client = MultiServerMCPClient({
            "nutrition": {
                "url": "https://my-nutrition-server.onrender.com/mcp",
                "transport": "streamable_http"
            }
        })
        tools = await client.get_tools()
        return tools
    except Exception as e:
        print(f"Error fetching tools: {e}")
        return []

# Create Graph Nodes

def Identify_foods(state: CalorieState):
    """Identifies food items asynchronously."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    part = genai_types.Part.from_bytes(data=state["image_bytes"], mime_type=state["mime"])
    prompt = """
    You are analyzing an image to identify food items. Follow these rules:
    1. List all visible food items clearly.
    - Mandatory to specify quantity (e.g., 2 bananas, 1 slice of bread).
    - Mention size/type if relevant (e.g., medium apple, large orange).
    2. If unclear, ask user to upload a clearer image.
    3. If no food, tell the user it's not a food image.
    4. Output structured as:
    Food Items:
    - <food item> (<quantity>, <size/type>)
    """
    response = client.models.generate_content(model="gemini-1.5-flash", contents=[part, prompt])
    return {"food_items": response.text}

async def fetch_calories(state: CalorieState):
    """Fetches calories asynchronously."""
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_API_KEY)
        tools = await get_tools()
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt="""You are a nutrition assistant. Use the nutrition_fetch tool to find calories 
                     and proteins. Return only nutrition facts, no extra explanations."""
        )

        food_query = state["food_items"]
        prompt = f"""For the following food items: {food_query}
        1. Use the nutrition_fetch tool for each food item.
        2. Extract calories and protein.
        3. List each item with calories/protein.
        4. Show totals at the end.
        5. Use bullet points only.
        """
        response = await agent.ainvoke({"messages": [("human", prompt)]})
        final_response = response["messages"][-1].content
        return {"result": final_response}
    except Exception as e:
        print(f"Error in fetch_calories: {e}")
        return {"result": "Failed to fetch calories."}

async def user_query_chatbot(state: CalorieState):
    """Handles user queries asynchronously."""
    user_message = state.get("user_query")
    if not user_message:
        return {"user_result": state.get("result", "No result yet.")}

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_API_KEY)
    tools = await get_tools()
    chatbot = create_react_agent(
        model=llm,
        tools=tools,
        prompt="""You are a nutrition assistant. 
        Use the previous nutrition analysis to answer user queries.
        use wiki_search tool if needed or response on you own.  
        If the user points out missing or incorrect food items, 
        recalculate only for those items and update the totals.
        You can provide answers to user query if they ask about the
        food,nutrition or you can even answer personal questions."""

    )

    context = state.get("result")
    response = await chatbot.ainvoke({
        "messages": [("human", f"Previous nutrition analysis: {context}\n\nUser question: {user_message}")]
    })
    final_response = response["messages"][-1].content
    return {"user_result": final_response}

# Graph Intitialization
def create_calorie_graph():
    builder = StateGraph(CalorieState)

    # Nodes
    builder.add_node("identify_foods", Identify_foods)
    builder.add_node("fetch_calories", fetch_calories)
    builder.add_node("user_query", user_query_chatbot)

    # set entry point
    def start_branch(state: CalorieState) -> str:
        if state.get("user_query") and state.get("result"):
            return "user_query"
        elif state.get("image_bytes") and state.get("mime"):
            return "identify_foods"
        elif state.get("user_query"):
            return "user_query"
        else:
            return "END"

    # conditional edges
    builder.add_conditional_edges(
        START,
        start_branch,
        {"identify_foods": "identify_foods", "user_query": "user_query", "END": END}
    )

    # edges
    builder.add_edge("identify_foods", "fetch_calories")
    builder.add_edge("fetch_calories", END)
    builder.add_edge("user_query", END)

    return builder.compile(checkpointer=memory)

calorie_graph = create_calorie_graph()