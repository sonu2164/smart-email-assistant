import streamlit as st
from agent import get_agent

# Page configuration
st.set_page_config(
    page_title="Smart Email Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False

# Main chat area
st.title("Smart Email Assistant")

# Create a container for the agent's thinking process
thinking_container = st.container()

# Initialize agent only once
if not st.session_state.agent_initialized:
    with st.spinner("Initializing agent..."):
        st.session_state.agent = get_agent(thinking_container)
        st.session_state.agent_initialized = True

# Function to process user input
def process_input(query):
    if query:
        # Add user message to chat history
        st.session_state.messages.append(("user", query))
        
        # Get response from agent
        with thinking_container:
            response = st.session_state.agent.run(query)
        
        # Add assistant response to chat history
        st.session_state.messages.append(("assistant", response))

# Sidebar with quick actions
with st.sidebar:
    st.title("Quick Actions")
    st.markdown("---")
    
    # Quick action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📨 Summarize Unread", key="summarize", help="List and summarize unread emails"):
            process_input("List unread threads and summarize daily emails.")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clean Marketing", key="clean", help="Delete old marketing emails"):
            process_input("Trash marketing emails older than 30 days.")
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏷️ Categorize", key="categorize", help="Auto-categorize your inbox"):
            process_input("Categorize unread emails into Promotions, Work, Personal.")
            st.rerun()
    
    with col2:
        if st.button("⚙️ Create Rule", key="rule", help="Create a Gmail filter"):
            process_input("Create a Gmail filter: if from newsletters, archive.")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This assistant helps you manage your Gmail account.
    
    It can:
    - Summarize emails
    - Clean up your inbox
    - Create filters
    - And more!
    """)

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role, content = message
        
        # Display the message with Streamlit components
        with st.chat_message(role):
            st.write(content)

# Chat input
user_input = st.chat_input("Type your message here...", key="user_input")

# If the chat input is used directly (when Enter is pressed)
if user_input:
    process_input(user_input)
    st.rerun()
