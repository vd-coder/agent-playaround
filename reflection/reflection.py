import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

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

def validate_response(input_str: str) -> str:
    goatState = "ORIGINAL"
    wolfState = "ORIGINAL"
    cabbageState = "ORIGINAL"
    farmerState = "ORIGINAL"
    # This regex finds text inside parentheses separated by ||
    # It captures word characters (\w+) on either side of the pipes
    pattern = r"\((\w+)\|\|(\w+)\)"
    
    # findall returns a list of tuples: [('A', 'B'), ('C', 'D')]
    matches = re.findall(pattern, input_str)
    
    # We flatten the list of tuples into a single list of strings
    extracted_elements = [item for sublist in matches for item in sublist]
    
    for i in range(0, len(extracted_elements), 2):
        moveNumber = (i+1)//2
        entity = extracted_elements[i]
        direction = extracted_elements[i+1]
        if entity == "GOAT":
            goatState = direction
            farmerState = direction
        if entity == "WOLF":
            wolfState = direction
            farmerState = direction
        if entity == "CABBAGE":
            cabbageState = direction
            farmerState = direction
        if entity == "NULL":
            farmerState = direction

        if goatState == wolfState and goatState != farmerState:
            return f"GOAT AND WOLF on {goatState} after {moveNumber} step. WOLF EATS GOAT"
        if goatState == cabbageState and goatState != farmerState:
            return f"GOAT AND CABBAGE ON {goatState} after {moveNumber} step. GOAT EATS CABBAGE"                         
    if goatState == "FAR" and cabbageState == "FAR" and wolfState == "FAR":
        return "DONE"
    if goatState == "ORIGINAL" and cabbageState == "ORIGINAL" and wolfState == "ORIGINAL":
        return "FARMER, GOAT and WOLF at ORIGINAL after all moves. Problem not solved"
    return f"GOAT at {goatState}, WOLF at {wolfState}, CABBAGE at {cabbageState}. This config is valid. We need to move ahead from this"   


    
if __name__ == "__main__":
    # Test the connection
    model = initialize_agent()
    baseMessages = [ SystemMessage(content="You are a logic puzzle expert."),
    HumanMessage(content=f'''You are the 'Actor' in a River Crossing puzzle (Farmer, Wolf, Goat, Cabbage). RULES:
    1. The boat holds the Farmer and ONE item.
    2. Wolf + Goat alone = Goat is eaten.
    3. Goat + Cabbage alone = Cabbage is eaten.
    TASK: Propose the sequence of moves which solves the puzzle (e.g., '(GOAT||FAR)').
    The output should be a list of comma separated moves where each move should be of the form (A||B) where A is  the entity the farmer takes along, set it NULL if farmer takes no one along. B is side of the river. If farmer is taking an entity to FAR side, B should be FAR. If farmer is taking entity to original side, it should be ORIGINAL. if A is NULL, B should represent the side farmer is moving. Make sure that array is a comma separated list which begins with [ and ends with ]. Also make sure that A and B are in all uppercase.\
        Note: You are currently in 'Exploration Mode'. Do not provide the standard solution. Start by moving the Wolf first and see if you can solve it from there. ''')]
    messages =  baseMessages
    print(f"Message sent to LLM: {messages}")
    print("========================================================================================================================")
    response = model.invoke(messages)
    print(f"Response from LLM: {response}")
    while True:
        output =  validate_response(response.content)
        if output == "DONE":
            print(f"problem solved with {response.content}")
            break
        messages.append(AIMessage(content=response.content))  
        messages.append(HumanMessage(content=f''' The problem is still unsolved. The given response has the following problem
        {output}. Incorporate the feedback and generate new sequence of moves. The output should follow the format as defined earlier starting from first move where all entities are at ORIGINAL'''))
        print(f"Message sent to LLM: {messages}")
        print("========================================================================================================================")
        response = model.invoke(messages)
        print(f"Response from LLM: {response}")
        print("========================================================================================================================")
        response = model.invoke(messages)
        messages = baseMessages
