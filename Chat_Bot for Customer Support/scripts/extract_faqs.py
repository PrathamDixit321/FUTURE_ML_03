"""Extract question-answer FAQ pairs from a conversation CSV using simple heuristics.

Usage:
    python scripts/extract_faqs.py input.csv --out data/derived_faqs.csv --top 50

The script looks for rows where a customer message ends with '?' and the next agent
message is treated as the answer.
"""
import argparse
import csv
from collections import Counter
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def detect_columns(header):
    header = [h.lower() for h in header]
    sender_col = None
    text_col = None
    for c in ['sender', 'from', 'role']:
        if c in header:
            sender_col = header.index(c)
            break
    for c in ['message', 'text', 'utterance']:
        if c in header:
            text_col = header.index(c)
            break
    return sender_col, text_col


def extract_pairs(infile):
    pairs = []
    with open(infile, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        header = next(reader)
        sender_col, text_col = detect_columns(header)
        rows = list(reader)
        for i, row in enumerate(rows[:-1]):
            try:
                sender = row[sender_col].lower() if sender_col is not None else ''
                # join remaining columns to handle unquoted commas
                text = ' '.join(row[text_col:]).strip() if text_col is not None else ''
            except Exception:
                continue
            if text and text.strip().endswith('?') and ('user' in sender or 'customer' in sender or 'client' in sender or sender == ''):
                # find next agent response
                for j in range(i+1, min(i+6, len(rows))):
                    next_sender = rows[j][sender_col].lower() if sender_col is not None else ''
                    next_text = ' '.join(rows[j][text_col:]).strip() if text_col is not None else ''
                    if 'agent' in next_sender or 'support' in next_sender or 'staff' in next_sender:
                        pairs.append((text.strip(), next_text.strip()))
                        break
    return pairs


def main():
    p = argparse.ArgumentParser()
    p.add_argument('infile')
    p.add_argument('--out', default='data/derived_faqs.csv')
    p.add_argument('--top', type=int, default=50)
    args = p.parse_args()

    pairs = extract_pairs(args.infile)
    counter = Counter(pairs)
    most = counter.most_common(args.top)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['question', 'answer'])
        for (q, a), _ in most:
            writer.writerow([q, a])
    print(f'Wrote {len(most)} FAQ pairs to {args.out}')


if __name__ == '__main__':
    main()
