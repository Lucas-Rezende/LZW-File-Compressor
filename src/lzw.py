import os
import io
import time
import sys

from compact_trie import *
from compress_and_decompress import *

class LZW:
    def __init__(self, max_bits=16):
        self.max_bits = max_bits
        self.max_code = (1 << max_bits) - 1
        self.reset()

    def reset(self):
        self.dicionario_size = 256
        self.trie = CompactTrie(self.max_code)
        self.start = time.time()

        for i in range(256):
            self.trie.insert(bytes([i]), i)

        self.stats = {
            "start": self.start,
            "tamanho_original": 0,
            "tamanho_comprimido": 0,
            "dictionary_memory": sys.getsizeof(self.trie),
            "total_time": 0,
            "compression_ratio": 0,
        }

    def compress(self, input_bytes):
        prefixo = bytes()
        self.codes = []
        self.stats["tamanho_original"] = len(input_bytes)

        for byte in input_bytes:
            current_word = prefixo + bytes([byte])
            found_code = self.trie.search(current_word)

            if found_code is not None:
                prefixo = current_word
            else:
                prefix_code = self.trie.search(prefixo)
                if prefix_code is not None:
                    self.codes.append(prefix_code)

                self.trie.insert(current_word, self.dicionario_size)
                self.dicionario_size += 1

                prefixo = bytes([byte])

        if prefixo:
            prefix_code = self.trie.search(prefixo)
            if prefix_code is not None:
                self.codes.append(prefix_code)

        self.stats["tamanho_comprimido"] = len(self.codes) * (self.max_bits // 8)
        self.stats["compression_ratio"] = self.stats["tamanho_original"] / self.stats["tamanho_comprimido"] if self.stats["tamanho_comprimido"] > 0 else 0
        self.stats["compression_ratio"] = self.stats["tamanho_original"] / self.stats["tamanho_comprimido"] if self.stats["tamanho_comprimido"] > 0 else 0

        self.stats["total_time"] = time.time() - self.stats["start"]

        return self.codes

    def decompress(self, compressed_codes):
        reverse_dicionario = {(i & ((1 << self.get_bits_for_code()) - 1)): bytes([i]) for i in range(256)}
        prefixo = reverse_dicionario[compressed_codes[0]]
        result = bytearray(prefixo)

        for codigo in compressed_codes[1:]:
            if codigo in reverse_dicionario:
                entry = reverse_dicionario[codigo]
            else:
                entry = prefixo + prefixo[:1]

            result.extend(entry)
            reverse_dicionario[len(reverse_dicionario)] = prefixo + entry[:1]
            prefixo = entry

        self.stats["detamanho_comprimido"] = len(result)

        self.stats["total_time"] = time.time() - self.stats["start"]

        return bytes(result)

    def get_bits_for_code(self):
        return self.max_bits

    def print_stats(self):
        print("Estatísticas de Compressão:")
        print(f" - Tamanho do arquivo original: {self.stats['tamanho_original']} bytes")
        print(f" - Tamanho do arquivo comprimido: {self.stats['tamanho_comprimido']} bytes")
        print(f" - Taxa de Compressão: {self.stats['compression_ratio']:.2f}")
        print(f" - Tempo total de execução: {self.stats['total_time']:.4f} segundos")

def LZW_not_fixed_compress(input_file_path, max_bits=12):
    base_name = os.path.basename(input_file_path)
    compressed_file_path = os.path.splitext(base_name)[0] + '.lzw'

    with open(input_file_path, 'rb') as input_file, open(compressed_file_path, 'wb') as output_file:
        dicionario = CompactTrie2()
        for i in range(256):
            dicionario[str(bytes([i]))] = i
        prefixo = bytes()
        current_bits = 9
        dicionario_limited = False
        dic_size = 256
        
        buffer = 0
        bits_in_buffer = 0

        while True:
            byte = input_file.read(1)
            if not byte:
                break

            byte = byte[0]
            if dicionario[str(prefixo + bytes([byte]))] != None:
                prefixo += bytes([byte])
            else:
                code = dicionario[str(prefixo)]
                buffer |= (code << bits_in_buffer)
                bits_in_buffer += current_bits

                while bits_in_buffer >= 8:
                    output_file.write(bytes([buffer & 0xFF]))
                    buffer >>= 8
                    bits_in_buffer -= 8

                if not dicionario_limited:
                    dicionario[str(prefixo + bytes([byte]))] = dic_size
                    dic_size += 1

                if dic_size >= ((1 << current_bits) - 1):
                    if current_bits < max_bits:
                        current_bits += 1
                    else:
                        dicionario_limited = True
            
                prefixo = bytes([byte])

        if prefixo:
            code = dicionario[str(prefixo)]
            buffer |= (code << bits_in_buffer)
            bits_in_buffer += current_bits

            while bits_in_buffer >= 8:
                output_file.write(bytes([buffer & 0xFF]))
                buffer >>= 8
                bits_in_buffer -= 8

        output_file.write(bytes([max_bits]))

    print(f"Arquivo comprimido gerado: {compressed_file_path}")

def decompress_file_not_fixed(input_file_path, output_file_path):
    # Lê o arquivo comprimido
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        compressed_data = input_file.read()
        max_bits = compressed_data[-1]
        size_atual = 9
        possiveis = ((1 << size_atual) - 1) - 256
        lidos = 0

        bit_stream = io.BytesIO(compressed_data[:-1])

        buffer = 0
        bits_in_buffer = 0
        compressed_codes = []

        reverse_dicionario = {i: bytes([i]) for i in range(256)}

        while True:
            byte = bit_stream.read(1)
            if not byte:
                break

            buffer |= (ord(byte) << bits_in_buffer)
            bits_in_buffer += 8

            while bits_in_buffer >= size_atual:
                code = buffer & ((1 << size_atual) - 1)
                compressed_codes.append(code)
                lidos += 1
                buffer >>= size_atual
                bits_in_buffer -= size_atual

                if lidos == possiveis:
                    if size_atual < max_bits:
                        size_atual += 1
                        possiveis = ((1 << size_atual) - 1) - 256

        prefixo = reverse_dicionario[compressed_codes.pop(0)]
        output_file.write(prefixo)

        for codigo in compressed_codes:
            if codigo in reverse_dicionario:
                entry = reverse_dicionario[codigo]
            else:
                entry = prefixo + prefixo[:1]

            output_file.write(entry)

            if len(reverse_dicionario) <= ((1 << max_bits) - 1):
                reverse_dicionario[len(reverse_dicionario)] = prefixo + entry[:1]

            prefixo = entry

    print(f"Arquivo descomprimido gerado: {output_file_path}")

def handle_file(file_path, lzw_compressor):
    if file_path.endswith('.lzw'):
        decompressed_file_path = os.path.splitext(file_path)[0] + '_decompressed' + os.path.splitext(file_path)[1]
        decompress_file(file_path, decompressed_file_path, lzw_compressor)
    else:
        compressed_file_path = compress_file(file_path, lzw_compressor)
        
def handle_file_2(file_path, quntbits=None):
    if file_path.endswith('.lzw'):
        decompressed_file_path = os.path.splitext(file_path)[0] + '_decompressed' + os.path.splitext(file_path)[1]
        decompress_file_not_fixed(file_path, decompressed_file_path)
    else:
        LZW_not_fixed_compress(file_path, quntbits)