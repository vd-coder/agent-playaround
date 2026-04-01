import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from langchain_core.tools import tool

# from langchain.agents import create_tool_calling_agent, AgentExecutor

def initialize_agent():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Did you create the .env file?")

    # 3. Initialize the model (LangChain automatically looks for GOOGLE_API_KEY 
    # in the background, but passing it explicitly is cleaner)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.7,
        google_api_key=api_key 
    )
    return llm

@tool
def search_information(query: str) -> str:
    """
    Use this tool to answer any factual information. Finds factual info. IMPORTANT: Use only short keywords  as the query. Do not use full sentences.
    """
    print(f"\n--- 🛠️ Tool Called: search_information with query: '{query}' ---")
    # Simulate a search tool with a dictionary of predefined results.
    simulated_results = {
        "weather in london": "The weather in London is currently cloudy with a temperature of 15°C.",
        "capital of france": "The capital of France is Paris.",
        "population of earth": "The estimated population of Earth is around 8 billion people.",
        "tallest mountain": "Mount Everest is the tallest mountain above sea level.",
        "default": f"Simulated search result for '{query}': No specific information found, but the topic seems interesting."
    }
    result = simulated_results.get(query.lower(), simulated_results["default"])
    print(f"--- TOOL RESULT: {result} ---")
    return result

tools = [search_information]

def agent_with_tools(query: str):
    llm = initialize_agent()
    messages = [SystemMessage(content = "You are an helpful assistant"),
    HumanMessage(content = query)]
    print(f"--- Tools available to LLM: {[t.description for t in tools]} ---")
    resp = llm.invoke(messages, tools = tools)
    print(resp)
    if resp.tool_calls:
        tool_call = resp.tool_calls[0]
        print(tool_call)
        tool_args = tool_call.get('args').get('query')
        output = search_information.invoke(tool_args)
        print(output)
    elif resp.content:
        print("LLM STOPPED")
        print(resp.content)    
    

# def inbuilt_agent_with_tools(query: str):
#     llm = initialize_agent()
#         # Create the agent, binding the LLM, tools, and prompt together.
#     agent = create_tool_calling_agent(llm, tools, agent_prompt)

#     # AgentExecutor is the runtime that invokes the agent and executes the chosen tools.
#     # The 'tools' argument is not needed here as they are already bound to the agent.
#     agent_executor = AgentExecutor(agent=agent, verbose=True)  

#     response =  agent_executor.invoke({"input": query}) 

#     print(respomse)

if __name__ == "__main__":
    agent_with_tools("How many people live in earth?")
    # inbuilt_agent_with_tools("What is the capital of France?")