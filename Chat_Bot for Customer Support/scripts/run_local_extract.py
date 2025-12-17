"""Run FAQ extractor on all CSV files in a local directory.

Usage: python scripts/run_local_extract.py data/raw --out data/derived_faqs.csv
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('indir', help='Input directory with CSVs')
    p.add_argument('--out', default='data/derived_faqs.csv')
    p.add_argument('--pattern', default='*.csv')
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.indir, args.pattern)))
    if not files:
        print('No CSV files found in', args.indir)
        return
    for f in files:
        print('Processing', f)
        os.system(f'python scripts/extract_faqs.py "{f}" --out "{args.out}"')


if __name__ == '__main__':
    main()
