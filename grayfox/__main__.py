import argparse
import sys
from dotenv import load_dotenv
from .service import generate, ConfigurationError, ProviderError

def main():
    load_dotenv(override=False)
    parser = argparse.ArgumentParser(description='Gray Fox AI; live calls may incur charges')
    parser.add_argument('--provider', choices=['anthropic', 'openai'])
    parser.add_argument('--max-tokens', type=int, default=512)
    args = parser.parse_args()
    prompt = sys.stdin.read(12001)
    try:
        print(generate(prompt, args.provider, max_tokens=args.max_tokens))
    except (ConfigurationError, ProviderError, ValueError) as exc:
        parser.exit(2, f'{exc}\n')

if __name__ == '__main__':
    main()
