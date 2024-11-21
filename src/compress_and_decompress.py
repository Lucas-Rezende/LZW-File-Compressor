import io, os

def compress_file(input_file_path, lzw_compressor):
    with open(input_file_path, 'rb') as f:
        input_data = f.read()

    compressed_codes = lzw_compressor.compress(input_data)

    bit_stream = io.BytesIO()

    buffer = 0
    bits_in_buffer = 0
    for code in compressed_codes:
        buffer |= (code << bits_in_buffer)
        bits_in_buffer += lzw_compressor.get_bits_for_code()

        while bits_in_buffer >= 8:
            bit_stream.write(bytes([buffer & 0xFF]))
            buffer >>= 8
            bits_in_buffer -= 8

    if bits_in_buffer > 0:
        bit_stream.write(bytes([buffer & 0xFF]))

    bit_stream.write(bytes([lzw_compressor.max_bits]))

    base_name = os.path.basename(input_file_path)
    compressed_file_path = os.path.splitext(base_name)[0] + '.lzw'

    with open(compressed_file_path, 'wb') as f:
        f.write(bit_stream.getvalue())

    print(f"Arquivo comprimido gerado: {compressed_file_path}")
    return compressed_file_path

def decompress_file(input_file_path, output_file_path, lzw_compressor):
    with open(input_file_path, 'rb') as f:
        compressed_data = f.read()

    initial_bits = compressed_data[-1]
    compressed_codes = []
    buffer = 0
    bits_in_buffer = 0

    bit_stream = io.BytesIO(compressed_data[0:-1])

    while True:
        byte = bit_stream.read(1)
        if not byte:
            break
        buffer |= ord(byte) << bits_in_buffer
        bits_in_buffer += 8

        while bits_in_buffer >= initial_bits:
            code = buffer & ((1 << initial_bits) - 1)
            compressed_codes.append(code)
            buffer >>= initial_bits
            bits_in_buffer -= initial_bits

    decompressed_data = lzw_compressor.decompress(compressed_codes)

    with open(output_file_path, 'wb') as f:
        f.write(decompressed_data)

    print(f"Arquivo descomprimido gerado: {output_file_path}")