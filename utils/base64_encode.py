#!/usr/bin/env python3
"""
Base64 encoding utility for Kubernetes secrets preparation
"""

import base64
import argparse
import sys


def encode_to_base64(input_str):
    """Encode a string to base64"""
    if isinstance(input_str, str):
        input_bytes = input_str.encode('utf-8')
    else:
        input_bytes = input_str
    encoded_bytes = base64.b64encode(input_bytes)
    return encoded_bytes.decode('utf-8')


def decode_from_base64(encoded_str):
    """Decode a base64 string"""
    decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
    return decoded_bytes.decode('utf-8')


def encode_file_to_base64(file_path):
    """Encode file contents to base64"""
    with open(file_path, 'rb') as f:
        file_content = f.read()
    encoded_bytes = base64.b64encode(file_content)
    return encoded_bytes.decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description='Base64 encoding utility for Kubernetes secrets')
    parser.add_argument('--encode', '-e', help='String to encode to base64')
    parser.add_argument('--decode', '-d', help='Base64 string to decode')
    parser.add_argument('--encode-file', '-f', help='File to encode to base64')
    parser.add_argument('--secret', '-s', nargs=2, metavar=('KEY', 'VALUE'),
                        help='Create a Kubernetes secret entry (key and value)')

    args = parser.parse_args()

    if args.encode:
        result = encode_to_base64(args.encode)
        print(result)
    elif args.decode:
        try:
            result = decode_from_base64(args.decode)
            print(result)
        except Exception as e:
            print(f"Error decoding: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.encode_file:
        try:
            result = encode_file_to_base64(args.encode_file)
            print(result)
        except FileNotFoundError:
            print(f"File not found: {args.encode_file}", file=sys.stderr)
            sys.exit(1)
    elif args.secret:
        key, value = args.secret
        encoded_value = encode_to_base64(value)
        print(f"{key}: {encoded_value}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()