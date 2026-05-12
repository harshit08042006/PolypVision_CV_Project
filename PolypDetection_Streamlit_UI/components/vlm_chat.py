"""VLM Assistant chat component integrated with real VLM backend."""
import streamlit as st
from vlm_query import query_vlm


def _on_send():
    """Callback to handle sending a message and clearing the input correctly."""
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
    if "vlm_input_text" not in st.session_state:
        st.session_state.vlm_input_text = ""
    if "vlm_clear_input" not in st.session_state:
        st.session_state.vlm_clear_input = False

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
        # Clear input if requested
        input_value = "" if st.session_state.vlm_clear_input else st.session_state.vlm_input_text
        user_text = st.text_input(
            "Ask the VLM",
            value=input_value,
            placeholder="Ask: What can be done now?" if not is_busy else "Processing...",
            key="vlm_input_text",
            label_visibility="collapsed",
            disabled=is_busy,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_send:
        btn_label = "✈ Send" if not is_busy else "..."
        if st.button(btn_label, key="vlm_send", disabled=is_busy):
            user_input = st.session_state.vlm_input_text
            if user_input.strip():
                st.session_state.vlm_current_query = user_input  # Save query before clearing
                st.session_state.vlm_busy = True
                st.session_state.vlm_clear_input = False  # Will set to True after response
                print(f"[VLM CHAT] Button clicked - Query saved: {user_input[:30]}...")
                st.rerun()
        else:
            # If button wasn't clicked but we're not busy and clear flag is set, reset it
            if not is_busy and st.session_state.vlm_clear_input:
                st.session_state.vlm_clear_input = False

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle VLM response (separate from UI rendering) ──
    if st.session_state.vlm_busy and st.session_state.vlm_current_query:
        user_query = st.session_state.vlm_current_query
        print(f"[VLM CHAT] Processing query: {user_query[:50]}...")
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        
        with st.spinner("🤖 VLM is thinking..."):
            try:
                print("[VLM CHAT] Building history...")
                history = st.session_state.chat_messages[:-1]
                print(f"[VLM CHAT] Calling query_vlm with history length: {len(history)}")
                response = query_vlm(user_query, history=history)
                print(f"[VLM CHAT] Got response: {response[:100]}...")
                st.success("✅ VLM responded!")
            except Exception as e:
                print(f"[VLM CHAT] Exception during query: {e}")
                import traceback
                traceback.print_exc()
                response = f"❌ Error: {str(e)}"
        
        print(f"[VLM CHAT] Adding response to chat: {response[:50]}...")
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.session_state.vlm_current_query = ""
        st.session_state.vlm_busy = False
        st.session_state.vlm_clear_input = True  # Flag to clear input on next render
        print("[VLM CHAT] About to rerun...")
        st.rerun()
