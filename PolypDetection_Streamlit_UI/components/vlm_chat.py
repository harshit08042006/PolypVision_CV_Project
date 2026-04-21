"""VLM Assistant chat component integrated with real VLM backend."""
import streamlit as st
from vlm_query import query_vlm


def _on_send():
    """Callback to handle sending a message and clearing the input."""
    u_input = st.session_state.vlm_input_text
    if u_input and u_input.strip():
        st.session_state.vlm_current_query = u_input
        st.session_state.vlm_input_text = ""
        st.session_state.vlm_busy = True


def render():
    """Render the VLM assistant chat panel."""
    # Initialize chat history and busy state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "vlm_busy" not in st.session_state:
        st.session_state.vlm_busy = False
    if "vlm_current_query" not in st.session_state:
        st.session_state.vlm_current_query = ""

    # Inject specific styles for THIS component's button
    st.markdown("""
        <style>
            /* Target any button that follows our unique vlm-header-mark */
            div:has(> .vlm-header-mark) ~ div button {
                background: linear-gradient(135deg, #00C6FF, #0072FF) !important;
                color: white !important;
                border-radius: 30px !important;
                border: none !important;
                font-size: 0.85rem !important;
                font-weight: 700 !important;
                height: 42px !important;
                box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3) !important;
                transition: all 0.3s ease !important;
            }
            div:has(> .vlm-header-mark) ~ div button:hover {
                transform: translateY(-2px) scale(1.05) !important;
                box-shadow: 0 8px 25px rgba(0, 114, 255, 0.5) !important;
                filter: brightness(1.1);
            }
            div:has(> .vlm-header-mark) ~ div button:disabled {
                background: #E2E8F0 !important;
                color: #94A3B8 !important;
                box-shadow: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ── Header ──
    st.markdown(
        """
        <div class="vlm-header-mark" style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div>
                <p style="font-weight:700;font-size:1rem;margin:0;">🌐 VLM Assistant</p>
                <p style="font-size:0.78rem;color:#6B7A8D;margin:2px 0 0;">Polyp-related Q&A · Grounded on detection + segmentation</p>
            </div>
            <span class="online-badge">● Online</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Chat messages ──
    chat_container = st.container(height=280)
    with chat_container:
        for msg in st.session_state.chat_messages:
            role = msg["role"]
            content = msg["content"]
            css_class = f"chat-msg chat-msg-{role}"
            st.markdown(
                f'<div class="{css_class}">{content}</div>',
                unsafe_allow_html=True,
            )
        
        if st.session_state.vlm_busy:
            st.markdown('<div class="chat-msg chat-msg-assistant">⌛ Assistant is thinking...</div>', unsafe_allow_html=True)

    # ── Input row ──
    col_input, col_send = st.columns([5, 2])
    is_busy = st.session_state.vlm_busy
    
    with col_input:
        st.markdown('<div class="vlm-input-container">', unsafe_allow_html=True)
        st.text_input(
            "Ask the VLM",
            placeholder="Ask: What can be done now?" if not is_busy else "Assistant is thinking...",
            key="vlm_input_text",
            label_visibility="collapsed",
            disabled=is_busy,
            on_change=_on_send # Trigger when Enter is pressed
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_send:
        btn_label = "✈ Send" if not is_busy else "..."
        st.button(btn_label, key="vlm_send", use_container_width=True, disabled=is_busy, on_click=_on_send)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Processing logic ──
    if st.session_state.vlm_busy:
        user_input = st.session_state.vlm_current_query
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            try:
                history = st.session_state.chat_messages[:-1]
                response = query_vlm(user_input, history=history)
            except Exception as e:
                response = f"[Error contacting VLM: {e}]"
                
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.session_state.vlm_current_query = ""
            st.session_state.vlm_busy = False
            st.rerun()
