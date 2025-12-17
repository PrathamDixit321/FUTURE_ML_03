import os
import pytest

from app.chatbot import Chatbot


def test_greeting():
    cb = Chatbot('data/sample_faqs.csv')
    resp = cb.get_response('Hi there')
    assert 'Hi' in resp['answer']


def test_faq_retrieval():
    cb = Chatbot('data/sample_faqs.csv')
    resp = cb.get_response('How do I reset my password?')
    assert resp['source'] in ('faq', 'openai')
    assert 'password' in resp['answer'].lower() or resp['source'] == 'openai'


def test_create_ticket(tmp_path):
    tickets_file = tmp_path / "tickets.csv"
    cb = Chatbot('data/sample_faqs.csv')
    cb.tickets_csv = str(tickets_file)
    ticket = cb.create_ticket('This is a test issue', contact='test@example.com')
    assert 'id' in ticket
    assert tickets_file.exists()
    contents = tickets_file.read_text(encoding='utf-8')
    assert 'This is a test issue' in contents
