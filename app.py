import streamlit as st
import requests
import json

# ------------ CONFIG ------------
st.set_page_config(
    page_title="AI Study Assistant", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for elegant styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3561 0%, #1f2544 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Title styling */
    h1 {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    
    /* Info box styling */
    .stAlert {
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.9);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 20px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    [data-testid="stFileUploader"] section {
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #667eea !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #5568d3 !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Backend API URL
API_URL = "http://localhost:8000"

# ------------ MAIN APP ------------
def main():
    # Header with emoji
    st.markdown("""
        <h1>🎓 AI Study Assistant</h1>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "answer_type" not in st.session_state:
        st.session_state.answer_type = "Short (2 Marks)"

    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 Document Upload")
        
        files = st.file_uploader(
            "Upload study materials",
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True,
            help="Upload PDF, DOCX, or TXT files"
        )
        
        btn = st.button("🚀 Index Files", type="primary")
        
        st.markdown("---")
        
        # Answer type selection
        st.markdown("### ✏️ Answer Format")
        answer_type = st.radio(
            "Select answer length:",
            ["Short (2 Marks)", "Medium (5 Marks)", "Detailed (10 Marks)", "Viva/Interview"],
            key="answer_type_radio",
            help="Choose how detailed you want the answers to be"
        )
        st.session_state.answer_type = answer_type
        
        st.markdown("---")
        
        # Session info and reset
        if st.session_state.session_id:
            st.success("✅ Session Active")
            st.caption(f"ID: {st.session_state.session_id[:8]}...")
            
        clear = st.button("🔄 Reset Session", type="secondary")
        
        if clear:
            if st.session_state.session_id:
                try:
                    requests.delete(f"{API_URL}/session/{st.session_state.session_id}")
                except:
                    pass
            st.session_state.session_id = None
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Upload clear, readable documents
        - Ask specific questions
        - Use answer format selector
        - Reset to start fresh
        """)

    # Handle file upload
    if btn and files:
        with st.spinner("📖 Processing documents..."):
            try:
                files_data = []
                for file in files:
                    files_data.append(
                        ("files", (file.name, file.getvalue(), file.type))
                    )
                
                response = requests.post(
                    f"{API_URL}/upload",
                    files=files_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.chat_history = []
                    st.success("✅ Documents indexed successfully!")
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Chat interface
    if st.session_state.session_id:
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])

        # Chat input
        question = st.chat_input("💬 Ask your question here...")
        if question:
            # Display user message
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(question)
            
            # Add to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })

            # Get response from backend
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={
                                "session_id": st.session_state.session_id,
                                "question": question,
                                "chat_history": st.session_state.chat_history[:-1],
                                "answer_type": st.session_state.answer_type
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            st.markdown(answer)
                            
                            # Add to history
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": answer
                            })
                        else:
                            error_msg = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Error: {error_msg}")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        # Welcome message
        st.markdown("""
            <div style='text-align: center; padding: 50px; background-color: rgba(255, 255, 255, 0.1); 
                        border-radius: 20px; margin: 20px;'>
                <h2 style='color: white;'>👋 Welcome to AI Study Assistant!</h2>
                <p style='color: white; font-size: 1.2rem;'>
                    Upload your study materials and start learning with AI-powered assistance.
                </p>
                <p style='color: white; margin-top: 20px;'>
                    📤 Upload files from the sidebar to begin
                </p>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()