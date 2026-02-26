import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. Setup & API Key Security
# ==========================================
# Access the API key securely from Streamlit's secrets management
# (You will need to set this in your Streamlit Cloud dashboard or in .streamlit/secrets.toml locally)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except KeyError:
    st.error("Error: GOOGLE_API_KEY not found in Streamlit secrets. Please configure it.")
    st.stop()

# ==========================================
# 2. Specific System Instruction
# ==========================================
# Define the persona and rules for the Scheduling System
system_instruction = """
You are an expert AI Scheduling Assistant. Your primary goal is to help the user manage their time, 
schedule appointments, resolve calendar conflicts, and optimize their daily routines. 

Follow these rules:
1. Always be polite, highly organized, and concise.
2. When asked to schedule an event, clearly confirm the Date, Time, Duration, and Title.
3. If the user provides overlapping events, proactively point out the conflict and suggest alternative times.
4. Format your responses using markdown (bullet points, bold text for times/dates) to make them easy to read.
"""

# Initialize the Gemini model with the system instruction
# Using gemini-2.5-flash as it is the recommended model for general text and reasoning tasks
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_instruction
)

# ==========================================
# 3. UI Setup
# ==========================================
st.set_page_config(page_title="Scheduling System AI", page_icon="📅")
st.title("📅 Scheduling System AI")
st.write("Welcome! I am your AI Scheduling Assistant. How can I help you organize your schedule today?")

# ==========================================
# 4. Session State Management
# ==========================================
# Initialize the chat history array if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the Gemini chat object to maintain conversation context on the API side
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display all previous chat messages from the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. Chat Interface
# ==========================================
# Capture user input from the chat input box
if prompt := st.chat_input("E.g., Schedule a 30-min sync with the marketing team tomorrow at 10 AM..."):
    
    # 1. Display the user's message in the UI
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Save the user's message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Send the message to the Gemini API and get the response
    with st.chat_message("assistant"):
        try:
            # We use a spinner to show the user that the AI is "thinking"
            with st.spinner("Checking schedule..."):
                response = st.session_state.chat_session.send_message(prompt)
                
            # Display the AI's response
            st.markdown(response.text)
            
            # Save the AI's response to session state
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"An error occurred while communicating with the AI: {e}")
