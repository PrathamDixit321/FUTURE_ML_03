import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.chatbot import Chatbot

cb = Chatbot('data/sample_faqs.csv')
cb.tickets_csv = 'test_tickets.csv'
if os.path.exists(cb.tickets_csv):
    os.remove(cb.tickets_csv)

ticket = cb.create_ticket('My app crashes when I click Save')
print('ticket:', ticket)
print('file exists:', os.path.exists(cb.tickets_csv))
print(open(cb.tickets_csv).read())
