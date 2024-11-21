import os
import io
import argparse

from compact_trie import *
from lzw import *

def main():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('input_file_path', type=str, help='Caminho do arquivo de entrada')
    parser.add_argument('--max_bits', type=int, default=12, help='Número máximo de bits')
    parser.add_argument('--dinamico', action='store_true', help='Dinâmico')
    parser.add_argument('--tests', action='store_true', help='Testes')

    args = parser.parse_args()

    if args.dinamico:
        handle_file_2(args.input_file_path, args.max_bits)
    else:
        lzw_compressor = LZW(args.max_bits)
        handle_file(args.input_file_path, lzw_compressor)
        
        if args.tests:
            lzw_compressor.print_stats()

if __name__ == "__main__":
    main()