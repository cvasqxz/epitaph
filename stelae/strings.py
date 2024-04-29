from string import ascii_uppercase, hexdigits
from functools import reduce

# https://stackoverflow.com/a/48984697

def divmod_excel(n):
	a, b = divmod(n, 26)
	if b == 0:
		return a - 1, b + 26
	return a, b


def decode_name(num):
	num += 1
	chars = []
	while num > 0:
		num, d = divmod_excel(num)
		chars.append(ascii_uppercase[d - 1])
	return ''.join(reversed(chars))


def encode_name(chars):
	return reduce(lambda r, x: r * 26 + x + 1, map(ascii_uppercase.index, chars), 0) - 1


def is_hex(s):
	try:
		int(s, 16)
		return True
	except ValueError:
		return False