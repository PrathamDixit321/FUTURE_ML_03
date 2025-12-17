import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.chatbot import Chatbot

cb = Chatbot('data/sample_faqs.csv')
print(cb.get_response('Hi there'))
print(cb.get_response('How do I reset my password?'))
