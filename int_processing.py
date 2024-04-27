def decode_LEB128(b):
	r = 0
	for i, e in enumerate(b):
		r = r + ((e & 0x7f) << (i * 7))
	return r

# LEB128 varints are encoded as sequence of bytes, 
# each of which has the most-significant bit set, except for the last.
def find_LEB128_sequence(s):
	int_seq = []
	buffer = b''

	for char in s:
		buffer += bytes([char])

		if char < 0x7f:
			int_seq.append(decode_LEB128(buffer))
			buffer = b''

	return int_seq
