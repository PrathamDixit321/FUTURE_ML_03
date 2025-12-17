import os
from dotenv import load_dotenv
import streamlit as st

from app.chatbot import Chatbot

load_dotenv()

FAQ_CSV = os.getenv('FAQ_CSV', 'data/sample_faqs.csv')

st.set_page_config(page_title='Support Chatbot')

if 'messages' not in st.session_state:
    st.session_state.messages = []

cb = Chatbot(FAQ_CSV)

st.title('Customer Support Chatbot')
st.write('Hi! Ask me anything — I can answer FAQs and escalate if needed.')

with st.sidebar:
    st.header('Settings')
    st.write('Use the environment variables or .env to set keys.')

for i, m in enumerate(st.session_state.messages):
    if m['role'] == 'user':
        st.markdown(f"**You:** {m['text']}")
    else:
        st.markdown(f"**Bot:** {m['text']}")
        meta = m.get('meta', {})
        if meta.get('offer_ticket'):
            ticket_key = f"ticket-{i}"
            if st.button('Create support ticket', key=ticket_key):
                # try to use the preceding user message as ticket text
                query_text = ''
                if i > 0 and st.session_state.messages[i-1]['role'] == 'user':
                    query_text = st.session_state.messages[i-1]['text']
                else:
                    query_text = m['text']
                ticket = cb.create_ticket(query_text)
                st.session_state.messages.append({'role': 'bot', 'text': f"Ticket created: {ticket['id']}. Our team will follow up.", 'meta': {'ticket': ticket}})
                st.experimental_rerun()

query = st.text_input('Your message', key='input')
if st.button('Send') and query:
    st.session_state.messages.append({'role': 'user', 'text': query})
    resp = cb.get_response(query, chat_history=[{'role': 'user', 'content': q['text']} for q in st.session_state.messages])
    st.session_state.messages.append({'role': 'bot', 'text': resp['answer'], 'meta': resp})
    st.experimental_rerun()
