"""Download a Kaggle dataset and extract CSVs for FAQ extraction.

Usage: python scripts/download_kaggle.py <dataset-identifier> [--file pattern] [--out data/raw]

Example dataset identifier: 'zynicide/wine-reviews' or 'owner/dataset-name'
"""
import argparse
import os
import sys
import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def ensure_kaggle_available():
    try:
        import kaggle
        return kaggle
    except Exception as e:
        print('kaggle package not installed or importable. Please install with `pip install kaggle`.')
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('dataset', help='Kaggle dataset identifier e.g. owner/dataset')
    p.add_argument('--file', help='Filename glob to extract (default: *.csv)', default='*.csv')
    p.add_argument('--out', help='Output directory', default='data/raw')
    args = p.parse_args()

    kaggle = ensure_kaggle_available()
    # Check for credentials
    cfg_path = os.path.expanduser('~/.kaggle/kaggle.json')
    if not os.path.exists(cfg_path) and not (os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY')):
        print('Kaggle credentials not found. Place kaggle.json in ~/.kaggle or set KAGGLE_USERNAME and KAGGLE_KEY env vars.')
        return

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    print(f'Downloading dataset {args.dataset} to {out_dir}...')
    try:
        kaggle.api.dataset_download_files(args.dataset, path=out_dir, unzip=True, quiet=False)
    except Exception as e:
        print('Error downloading dataset:', e)
        return

    # find matching files
    files = glob.glob(os.path.join(out_dir, args.file))
    if not files:
        print('No files matching', args.file, 'found in', out_dir)
    else:
        print('Found files:', files)
        # run extractor for each CSV file
        for f in files:
            print('Extracting FAQs from', f)
            os.system(f'python scripts/extract_faqs.py "{f}" --out data/derived_faqs.csv')


if __name__ == '__main__':
    main()
