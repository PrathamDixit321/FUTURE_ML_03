import os
import csv
import json
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None

import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


class Chatbot:
    def __init__(self, faq_csv: Optional[str] = None):
        self.faqs = []  # list of (question, answer)
        self.faq_questions = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.tickets_csv = os.getenv('TICKETS_CSV', 'tickets.csv')
        # Load FAQ(s): accept a single CSV path, a list of paths, or default files
        if isinstance(faq_csv, (list, tuple)):
            for path in faq_csv:
                if path and os.path.exists(path):
                    self.load_faqs(path)
        elif isinstance(faq_csv, str) and faq_csv:
            if os.path.exists(faq_csv):
                self.load_faqs(faq_csv)
        else:
            # try derived then sample
            for default in ['data/derived_faqs.csv', 'data/sample_faqs.csv']:
                if os.path.exists(default):
                    self.load_faqs(default)

    def create_ticket(self, user_query: str, contact: Optional[str] = None) -> dict:
        """Create a simple ticket stored in a CSV file and return ticket info."""
        from datetime import datetime
        import csv as _csv

        ticket_id = int(datetime.utcnow().timestamp())
        ticket = {
            'id': ticket_id,
            'query': user_query,
            'contact': contact or '',
            'status': 'open',
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        write_header = not os.path.exists(self.tickets_csv)
        with open(self.tickets_csv, 'a', newline='', encoding='utf-8') as fh:
            writer = _csv.DictWriter(fh, fieldnames=['id', 'query', 'contact', 'status', 'created_at'])
            if write_header:
                writer.writeheader()
            writer.writerow(ticket)
        return ticket

    def load_faqs(self, csv_path: str):
        # Try pandas first; fall back to Python csv reader on parse errors
        try:
            df = pd.read_csv(csv_path, engine='python', quotechar='"')
            # expected columns: question, answer
            self.faqs = list(zip(df['question'].astype(str).tolist(), df['answer'].astype(str).tolist()))
            self.faq_questions = [q for q, _ in self.faqs]
        except Exception:
            faqs = []
            import csv as _csv
            with open(csv_path, newline='', encoding='utf-8') as fh:
                reader = _csv.reader(fh)
                header = next(reader, None)
                for row in reader:
                    if not row:
                        continue
                    q = row[0]
                    a = ' '.join(row[1:]) if len(row) > 1 else ''
                    faqs.append((q, a))
            self.faqs = faqs
            self.faq_questions = [q for q, _ in self.faqs]
        if TfidfVectorizer and self.faq_questions:
            self.vectorizer = TfidfVectorizer().fit(self.faq_questions)
            self.tfidf_matrix = self.vectorizer.transform(self.faq_questions)

    def retrieve_faq(self, query: str) -> Tuple[Optional[str], float]:
        # return best answer and similarity score
        if self.vectorizer and self.tfidf_matrix is not None:
            q_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self.tfidf_matrix)[0]
            idx = int(np.argmax(sims))
            return self.faqs[idx][1], float(sims[idx])
        # fallback: keyword match
        for q, a in self.faqs:
            if any(tok.lower() in query.lower() for tok in q.split() if len(tok) > 3):
                return a, 0.5
        return None, 0.0

    def _is_greeting(self, text: str) -> bool:
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
        return any(text.lower().strip().startswith(g) for g in greetings)

    def get_response(self, query: str, chat_history: Optional[List[dict]] = None) -> dict:
        chat_history = chat_history or []
        # greeting
        if self._is_greeting(query):
            return {"answer": "Hi! How can I help you today?", "source": "greeting"}

        # try FAQ retrieval
        faq_answer, score = self.retrieve_faq(query)
        if faq_answer and score >= 0.65:
            return {"answer": faq_answer, "source": "faq", "score": score}

        # if OpenAI available, call it with context
        if OPENAI_API_KEY:
            system_prompt = (
                "You are a helpful customer support assistant. Answer concisely. "
                "If unsure, ask a clarifying question or offer to create a support ticket."
            )
            messages = [{"role": "system", "content": system_prompt}]
            if faq_answer:
                messages.append({"role": "system", "content": f"Relevant FAQ: {faq_answer}"})
            # include short chat history
            for msg in chat_history[-6:]:
                messages.append(msg)
            messages.append({"role": "user", "content": query})

            try:
                resp = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages, temperature=0.2)
                assistant_text = resp['choices'][0]['message']['content'].strip()
                # basic fallback detection
                if 'I don\'t know' in assistant_text or 'I am not sure' in assistant_text:
                    return {"answer": "Sorry, I am not sure about that. Would you like me to create a support ticket?", "source": "fallback", "offer_ticket": True}
                return {"answer": assistant_text, "source": "openai", "score": score}
            except Exception:
                return {"answer": "Sorry, I couldn't reach the AI service right now.", "source": "error", "offer_ticket": True}

        # final fallback
        if faq_answer:
            return {"answer": faq_answer, "source": "faq", "score": score}
        return {"answer": "Sorry, I didn't understand that. Could you rephrase or ask a different question?", "source": "fallback", "offer_ticket": True}


if __name__ == "__main__":
    cb = Chatbot('data/sample_faqs.csv')
    print(cb.get_response('Hi there'))
    print(cb.get_response('How do I reset my password?'))
