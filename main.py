import argparse
from src.agent import run_eda_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()
    result = run_eda_pipeline(args.csv)
    print(result['output'])
    # Save cleaned CSV + report