import os
from dotenv import load_dotenv
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from utils import get_all_tools

load_dotenv()

def get_agent(parent_container):
    # Use Gemini if specified, otherwise OpenAI
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            streaming=True,
            callbacks=[StreamlitCallbackHandler(parent_container=parent_container)],
        )
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            temperature=0,
            streaming=True,
            callbacks=[StreamlitCallbackHandler(parent_container=parent_container)],
        )
    
    # Get all tools
    tools = get_all_tools()
    
    # Set up memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Initialize agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )
    
    return agent
