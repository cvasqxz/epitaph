# https://github.com/mohanson/leb128

def encode_LEB128(i):
	"""Encode the int i using unsigned leb128 and return the encoded bytearray."""
	assert i >= 0
	r = []
	while True:
		byte = i & 0x7f
		i = i >> 7
		if i == 0:
			r.append(byte)
			return bytearray(r)
		r.append(0x80 | byte)


def decode_LEB128(b):
	"""Decode the signed leb128 encoded bytearray"""
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
