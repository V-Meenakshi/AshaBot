
#streamlit_app.py
import streamlit as st
import requests
import base64
import json
import os

# App configuration
st.set_page_config(
    page_title="Asha AI - Career Assistant for Women",
    page_icon="👩‍💼",
    layout="wide")

# Custom CSS for styling chat messages
st.markdown("""<style>
    /* User message styling */
    .user-message {
        background-color: #e6f7ff;
        border-radius: 10px;
        padding: 10px 15px;
        margin: 5px 0;
        border-left: 5px solid #1e88e5;
    }
    
    /* Assistant message styling */
    .assistant-message {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 10px 15px;
        margin: 5px 0;
        border-left: 5px solid #9c27b0;
    }
    
    /* Improve input field styling and remove red border */
    .stTextInput input {
        border-radius: 20px;
        padding: 10px 15px;
        border: 2px solid #9c27b0 !important;
        box-shadow: none !important;
    }
    
    /* Focus state for input - remove red outline */
    .stTextInput input:focus {
        box-shadow: none !important;
        border: 2px solid #9c27b0 !important;
    }
    
    /* Style the send button */
    .stButton button {
        border-radius: 20px;
        background-color: #9c27b0;
        color: white;
        border: none;
        padding: 10px 20px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f5f5f5;
        border-radius: 5px;
    }
    
    /* App header styling */
    h1 {
        color: #9c27b0;
    }
    
    h2 {
        color: #1e88e5;
    }
    
    /* Auth form styling */
    .auth-form {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    </style>""", unsafe_allow_html=True)

# Get API URL from environment variable or use default for local development
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_input" not in st.session_state:
    st.session_state.current_input = ""
if "process_message" not in st.session_state:
    st.session_state.process_message = False
if "example_selected" not in st.session_state:
    st.session_state.example_selected = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "password" not in st.session_state:
    st.session_state.password = None
if "show_login" not in st.session_state:
    st.session_state.show_login = True
if "connection_error" not in st.session_state:
    st.session_state.connection_error = None

# Authentication functions
def signup():
    st.title("Sign Up")
    
    # Show any connection errors
    if st.session_state.connection_error:
        st.error(f"Connection Error: {st.session_state.connection_error}")
        if st.button("Clear Error"):
            st.session_state.connection_error = None
    
    with st.container():
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        new_email = st.text_input("Email (optional)", key="signup_email")
        new_fullname = st.text_input("Full Name (optional)", key="signup_fullname")
        
        if st.button("Create Account", key="signup_button"):
            if not new_username or not new_password:
                st.error("Username and password are required.")
                return
                
            try:
                # Prepare user data
                user_data = {
                    "username": new_username,
                    "password": new_password,
                    "email": new_email if new_email else None,
                    "full_name": new_fullname if new_fullname else None
                }
                
                # Send request to create user
                response = requests.post(
                    f"{API_URL}/users",
                    json=user_data,
                    timeout=10  # Add timeout for better error handling
                )
                
                if response.status_code == 200:
                    st.success("Account created! Please sign in.")
                    st.session_state.show_login = True
                else:
                    error_detail = "Unknown error"
                    try:
                        error_detail = response.json().get("detail", "Unknown error")
                    except:
                        error_detail = response.text
                    st.error(f"Signup failed: {error_detail}")
            except requests.exceptions.ConnectionError as e:
                st.session_state.connection_error = f"Cannot connect to API server at {API_URL}. Please check if the backend is running and accessible."
                st.error(st.session_state.connection_error)
            except requests.exceptions.Timeout:
                st.error(f"Connection to {API_URL} timed out. Please try again later.")
            except Exception as e:
                st.error(f"Error during signup: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("Already have an account?")
        if st.button("Go to Login", key="goto_login"):
            st.session_state.show_login = True
            st.rerun()

def signin():
    st.title("Log In")
    
    # Show any connection errors
    if st.session_state.connection_error:
        st.error(f"Connection Error: {st.session_state.connection_error}")
        if st.button("Clear Error"):
            st.session_state.connection_error = None
    
    with st.container():
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        username = st.text_input("Username", key="signin_username")
        password = st.text_input("Password", type="password", key="signin_password")
        
        if st.button("Login", key="login_button"):
            if not username or not password:
                st.error("Username and password are required.")
                return
                
            try:
                # Test basic authentication by making a request to a protected endpoint
                auth_str = f"{username}:{password}"
                auth_bytes = auth_str.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                
                # Try to access a protected endpoint
                response = requests.post(
                    f"{API_URL}/jobs",  # Using jobs endpoint as a test
                    json={},  # Empty filter
                    headers={"Authorization": f"Basic {auth_b64}"},
                    timeout=10  # Add timeout for better error handling
                )
                
                if response.status_code == 200 or response.status_code == 401:  # 401 means authentication failed
                    if response.status_code == 200:
                        st.session_state.username = username
                        st.session_state.password = password
                        st.session_state.authenticated = True
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error(f"Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.session_state.connection_error = f"Cannot connect to API server at {API_URL}. Please check if the backend is running and accessible."
                st.error(st.session_state.connection_error)
            except requests.exceptions.Timeout:
                st.error(f"Connection to {API_URL} timed out. Please try again later.")
            except Exception as e:
                st.error(f"Error during login: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("Don't have an account?")
        if st.button("Create Account", key="goto_signup"):
            st.session_state.show_login = False
            st.rerun()

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.chat_history = []
    st.rerun()

# Function to handle example button clicks
def set_example_text(text):
    st.session_state.example_selected = text
    st.session_state.process_message = True

# Function to handle Send button clicks
def handle_send():
    if st.session_state.current_input.strip():
        user_input = st.session_state.current_input
        st.session_state.current_input = ""
        process_message(user_input)

# Function to process user input
def process_message(user_input):
    if user_input and st.session_state.authenticated:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Format chat history for API
        formatted_history = []
        for i in range(0, len(st.session_state.chat_history) - 1, 2):
            if i + 1 < len(st.session_state.chat_history):
                formatted_history.append([
                    st.session_state.chat_history[i]["content"],
                    st.session_state.chat_history[i + 1]["content"]
                ])
        
        # Send request to API with basic authentication header
        with st.spinner("Asha is thinking..."):
            try:
                # Create authentication header
                auth_str = f"{st.session_state.username}:{st.session_state.password}"
                auth_bytes = auth_str.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "query": user_input,
                        "chat_history": formatted_history
                    },
                    headers={"Authorization": f"Basic {auth_b64}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    asha_response = response_data["response"]
                    
                    # Add assistant response to chat history with any data
                    asha_message = {
                        "role": "assistant", 
                        "content": asha_response
                    }
                    
                    # Include any data for rendering
                    if "data" in response_data and response_data["data"]:
                        asha_message["data"] = response_data["data"]
                    
                    st.session_state.chat_history.append(asha_message)
                elif response.status_code == 401:
                    st.error("Your session has expired. Please login again.")
                    st.session_state.authenticated = False
                    st.rerun()
                else:
                    st.error(f"Failed to get response from Asha: {response.status_code}")
            except requests.exceptions.ConnectionError:
                error_msg = f"Cannot connect to API server at {API_URL}. Please check if the backend is running and accessible."
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": f"❌ {error_msg}"})
            except requests.exceptions.Timeout:
                error_msg = f"Connection to {API_URL} timed out. Please try again later."
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": f"❌ {error_msg}"})
            except Exception as e:
                st.error(f"Error communicating with API: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})

# Authentication check and handling
if not st.session_state.authenticated:
    st.title("Asha AI - Career Assistant for Women")
    st.markdown("""Your AI career assistant dedicated to helping women find jobs, discover events, and get career advice tailored to your professional journey.""")
    
    # Display either login or signup form based on session state
    if st.session_state.show_login:
        signin()
    else:
        signup()
    
    st.stop()  # Stop execution here if not authenticated

# Main app UI - Only shown when authenticated
st.title("Asha AI - Career Assistant for Women")
st.markdown("""Your AI career assistant dedicated to helping women find jobs, discover events, and get career advice tailored to your professional journey.""")

# User info in sidebar
with st.sidebar:
    st.markdown(f"*Logged in as:* {st.session_state.username}")
    if st.button("Logout"):
        logout()
    
    st.divider()
    
    st.header("Try asking about:")
    example_questions = [
        "Fetch jobs for software engineer role",
        "Show me HerKey events in Bangalore",
        "Are there any online return-to-work programs?",
        "What skills should I highlight for a software role?",
        "Are there any mentors from Google?",
        "How can I improve my resume?",
        "Find mentors for interview preparation"
    ]
    
    for i, question in enumerate(example_questions):
        if st.button(f"🔍 {question}", key=f"example_{i}"):
            set_example_text(question)

# Process example selection if needed
if st.session_state.process_message and st.session_state.example_selected:
    process_message(st.session_state.example_selected)
    st.session_state.example_selected = ""
    st.session_state.process_message = False

# Chat interface
st.header("Chat with Asha")

# Display chat history with styled backgrounds
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.info(f"👋 Hello, {st.session_state.username}! I'm Asha, your career assistant. How can I help you today?")
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", 
                unsafe_allow_html=True
            )
        else:
            # For assistant messages
            st.markdown(
                f"<div class='assistant-message'><strong>Asha:</strong> {message['content']}</div>", 
                unsafe_allow_html=True
            )
            
            if 'data' in message and 'jobs' in message['data'] and message['data']['jobs']:
                with st.expander("📊 Job Listings", expanded=True):
                    for job in message['data']['jobs']:
                        st.markdown(f"{job['role']} at {job['company_name']}")
                        
                        # Create two columns for job details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📍 Location: {job.get('location', 'Not specified')}")
                            st.write(f"🏠 Remote: {'Yes' if job.get('remote', False) else 'No'}")
                            if job.get('hire_time'):
                                st.write(f"⏱ Hire Time: {job.get('hire_time')}")
                        with col2:
                            if job.get('company_industry'):
                                st.write(f"🏢 Industry: {job.get('company_industry')}")
                            if job.get('company_size'):
                                st.write(f"🏢 Company Size: {job.get('company_size')}")
                            if job.get('salary'):
                                st.write(f"💰 Salary: {job.get('salary')}")
                        
                        if job.get('text'):
                            # Display full qualification text without truncation
                            st.write(f"📝 Description: {job.get('text')}")
                        
                        # Add apply link if available
                        if job.get('url'):
                            st.markdown(f"[Apply for this position]({job.get('url')})")
                            
                        st.markdown("---")
            
            # Show any event listings if available
            if 'data' in message and 'events' in message['data'] and message['data']['events']:
                with st.expander("📅 Upcoming Events", expanded=True):
                    for event in message['data']['events']:
                        st.markdown(f"### {event['name']}")
                        
                        # Create two columns for event details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📍 Location: {event.get('location', 'Not specified')}")
                            st.write(f"📆 Date: {event.get('start_date', 'N/A')} to {event.get('end_date', 'N/A')}")
                            st.write(f"⏰ Time: {event.get('timing', 'Not specified')}")
                        with col2:
                            st.write(f"🌐 Mode: {event.get('mode', 'Not specified')}")
                            if 'categories' in event and event['categories']:
                                st.write(f"🏷 Categories: {', '.join(event['categories'])}")
                        
                        # Display complete event description without truncation
                        if event.get('about'):
                            st.markdown("#### About this event")
                            st.write(event.get('about'))
                        
                        st.markdown("---")

            # Show any mentor listings if available
            if 'data' in message and 'mentors' in message['data'] and message['data']['mentors']:
                with st.expander("👩‍💼 Mentor Recommendations", expanded=True):
                    for mentor in message['data']['mentors']:
                        st.markdown(f"### {mentor['name']}")
                        st.markdown(f"{mentor['role']} at {mentor['company']}")
                        
                        # Create two columns for mentor details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📊 Bookings: {mentor.get('bookings', '0')}")
                        with col2:
                            if mentor.get('services') and len(mentor['services']) > 0:
                                services = [s.strip() for s in mentor['services']]
                                st.write(f"🛠 Services: {', '.join(services)}")
                        
                        st.markdown("---")       

# Side-by-side input and button
col1, col2 = st.columns([6, 1])  # Adjust the width ratio as needed

with col1:
    # Input field
    st.text_input(
        "Type your message...",
        key="input_field",
        value=st.session_state.current_input,
        on_change=lambda: None,  # No callback needed
        placeholder="Ask about jobs, mentors, events, or career advice...",
        label_visibility="collapsed"
    )
    # Update session state with the current input value
    st.session_state.current_input = st.session_state.input_field

with col2:
    if st.button("Send", use_container_width=True):
        handle_send()