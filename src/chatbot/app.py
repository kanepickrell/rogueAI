import streamlit as st
from typing import List, Tuple
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pipeline.doc_chunker import Chunk, DocumentChunker, DataPreprocessor
from pipeline.chunk_embedder import DocumentEmbedder
from model import ChatModel
import torch
from pathlib import Path
from transformers import TextStreamer
import time
# from unsloth import FastLanguageModel

with open("C:/repos/rogueAI/src/chatbot/squad_logo.md" , "r") as file:
    SQUADRON_LOGO_BASE64 = file.read()

RANGE_EVENTS = {
    "567_OGV": {"date": "2024-10-1", "description": "None"},
    "COMRADE_TURLA": {"date": "2023-01-01", "description": "None"},
    "MDS1": {"date": "2022-12-07", "description": "None."},
}

# Configure the default theme
st.set_page_config(
    page_title="318th RangeBot",
    page_icon=None,
    layout="wide"
)


@st.cache_resource
def load_model():
    model = ChatModel()
    if st.session_state.get('debug', False):
        return ChatModel.mock_model()   
    model.load()
    return model


def generate_response(model, tokenizer, context: str, query: str, max_length: int = 128) -> str:
    t0 = time.time()

    # Build conversation history string
    conversation_context = ""
    if st.session_state.conversation_history:
        conversation_context = "\n\nPrevious conversation:\n"
        for prev_q, prev_a in st.session_state.conversation_history:
            conversation_context += f"Q: {prev_q}\nA: {prev_a}\n"

    # Format messages to encourage direct answers
    messages = [
        {"role": "system", "content": "Provide direct, concise answers based on the given context without repeating the context itself."},
        {"role": "user", "content": f"Based on this context: {context}\n{conversation_context}\nQuestion: {query}"}
    ]

    t1 = time.time()
    # Apply chat template and tokenize
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    t2 = time.time()

    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=max_length,
        use_cache=True,
        temperature=1.5
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the answer part if possible
    if "assistant" in response.lower():
        response = response.split("assistant")[-1].strip()

    t3 = time.time()
    print(f"\nTimings:\nPrompt: {t1-t0:.2f}s\nTokenize: {t2-t1:.2f}s\nGenerate: {t3-t2:.2f}s")
    
    # return response
    return f"This is a mock response. Model is disabled for local testing.\nQuery: {query}\nContext length: {len(context)} characters"
 

def apply_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: white;
        padding: 2rem;
    }
    
    /* Logo styling - combined base styles */
    .squadron-logo-base {
        width: 60px;
        height: 60px;
        object-fit: contain;
    }
    
    .squadron-logo {
        composes: squadron-logo-base;
        margin-right: 10px;
    }
    
    .squadron-logo-header {
        composes: squadron-logo-base;
        margin-right: 15px;
        width: 80px;
        height: 80px;
        object-fit: contain;
    }

    /* Title container styling */
    .title-container {
        color: black;
        margin-top: -3.5rem;  
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def get_squadron_logo_html(size_class="squadron-logo"):
    return f'<img src="data:image/png;base64,{SQUADRON_LOGO_BASE64}" class="{size_class}" alt="Squadron Logo">'

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_history' not in st.session_state:
        # Preload some Q&A pairs
        st.session_state.conversation_history = [
        ]
    if 'selected_event' not in st.session_state:
        st.session_state.selected_event = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'model' not in st.session_state:
        st.session_state.model = load_model()

def get_event_context(event_name: str) -> str:
    """Get context string for selected event"""
    event = RANGE_EVENTS[event_name]
    return f"Event: {event_name}\nDate: {event['date']}\nDescription: {event['description']}"

def load_event_data(event_name):
    try:
        print(f"Loading data for event: {event_name}")
        preprocessor = DataPreprocessor()
        chunker = DocumentChunker(chunk_size=250, chunk_overlap=25)
        
        doc_path = Path(f'/content/data/{event_name}.md')
        print(f"Looking for file at: {doc_path}")
        print(f"File exists: {doc_path.exists()}")
        
        if not doc_path.exists():
            st.error(f"No data file found for {event_name}")
            return None
            
        with open(doc_path, 'r') as f:
            print(f"File content preview: {f.read()[:100]}")
            
        validated_docs = preprocessor.preprocess_documents([doc_path])
        chunks = chunker.process_documents(validated_docs)
        print(f"Number of chunks generated: {len(chunks)}")
        return chunks

    except Exception as e:
        st.error(f"Error processing {event_name}: {str(e)}")
        print(f"Full error: {str(e)}")
        return None

def display_event_tiles():
    with st.expander("Recent Events", expanded=False):
        event_cols = st.columns(3)
        
        for idx, (event_name, event_data) in enumerate(RANGE_EVENTS.items()):
            with event_cols[idx % 3]:
                is_selected = st.session_state.selected_event == event_name
                
                if st.button(
                    f"{event_name}",
                    key=f"event_{event_name}",
                    type="primary" if is_selected else "secondary",
                    use_container_width=True
                ):
                    if is_selected:
                        st.session_state.selected_event = None
                        st.session_state.event_chunks = None
                    else:
                        st.session_state.selected_event = event_name
                        st.session_state.event_chunks = load_event_data(event_name)
                    st.rerun()
                    
        return st.session_state.selected_event is not None

def display_chat_history():
    """Display chat messages with proper staggering"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=None if message["role"] == "assistant" else None):
            st.markdown(message["content"])

def type_text(text: str, container, speed=0.04):
    """Display text with typewriter effect"""
    placeholder = container.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(speed)
    return displayed_text

def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Header container
    with st.container():
        st.markdown(f"""
        <div class="title-container">
            {get_squadron_logo_html("squadron-logo-header")}
            <h1>RangeBot</h1>
        </div>
        <div style='background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h4 style='color: black; margin: 0;'>Explore recent training events using AI.</h4>
            <p style='color: black; margin: 0.5rem 0 0 0;'>Welcome Ranger! I am an experimental chatbot that can answer your questions regarding recent exercises and training events. Select an exercise below to discuss specific scenarios, lessons learned, and outcomes.</p>
        </div>
        """, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Display event tiles
    display_event_tiles()
    
    # Handle event selection
    current_event = st.session_state.selected_event

    if 'last_selected_event' not in st.session_state:
        st.session_state.last_selected_event = None

    # Display chat history
    display_chat_history()
    
    # Handle new event selection
    if current_event and current_event != st.session_state.last_selected_event:
        event_details = RANGE_EVENTS[current_event]
        selection_message = (
            f"Event Selected: {event_details['description']} | "
            f"Date: {event_details['date']} "
        )
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            displayed_text = type_text(selection_message, message_placeholder)
            message_placeholder.markdown(f"{displayed_text}")
            
        st.session_state.messages.append({"role": "assistant", "content": f"{selection_message}"})
        st.session_state.last_selected_event = current_event
    
    if not current_event:
        st.session_state.last_selected_event = None
    
    if prompt := st.chat_input("What would you like to know?", key="chat_input"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
            
        # Display assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            with response_placeholder:
                with st.spinner('Thinking...'):
                    if not current_event:
                        response = "You haven't selected an exercise yet. Please choose an event from the menu to start our conversation."
                    else:
                        embedder = DocumentEmbedder()
                        top_indices, top_scores, context = embedder.process_chunks(st.session_state.event_chunks, prompt)
                        context = " ".join(context)
                        
                        response = st.session_state.model.generate_response(
                            context,
                            prompt,
                            conversation_history=st.session_state.conversation_history
                        )
                        
                        # Store the Q&A pair in conversation history
                        st.session_state.conversation_history.append((prompt, response))
            
            # Display the response with typewriter effect
            type_text(response, response_placeholder)
                
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()