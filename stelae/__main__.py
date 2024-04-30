from binascii import unhexlify, hexlify
from argparse import ArgumentParser
from json import dumps

from constants import TAGS, OP_RETURN, OP_13 
from integers import find_LEB128_sequence
from strings import decode_name, is_hex


def main(args):
	if not is_hex(args.script) or len(args.script) % 2 != 0:
		print("error, malformed hex string")
		return

	script = unhexlify(args.script)

	# Find the first transaction output whose script pubkey
	# begins with OP_RETURN OP_13
	if not script.startswith(OP_RETURN + OP_13):
		print("error, script does not start with OP_RETURN OP_13")
		return

	p = 2

	while p < len(script):
		# The payload buffer is assembled by concatenating data pushes
		# Data pushes are opcodes 0 through 78 inclusive
		len_runestone = script[p]
		p += 1

		if len_runestone > 78:
			print("error, pushcode length invalid")
			return


		print(f"RUNESTONE FOUND: {hexlify(script[p:p+len_runestone])}")

		# A sequence of 128-bit integers are decoded
		# from the payload as LEB128 varints.
		int_seq = find_LEB128_sequence(script[p:p+len_runestone])
		print(f"LEB128 Integer sequence: {int_seq}")
		p += len_runestone

		last_id_height = 0
		last_id_txpos = 0
		mint = {'id': None, 'txpos': None}

		etching = False
		terms = False
		turbo = False

		runestone = {
			"edicts": [],
			'etching': None,
			"mint": None,
			"pointer": None
		}

		while len(int_seq) > 0:
			tag = int_seq.pop(0)
			print(f"tag: {tag} (valid = {tag in TAGS})")

			if not tag in TAGS:
				print(f"invalid tag found, this is a cenotaph")
				return

			if tag == 0:
				# Rune ID block heights and transaction indices
				# in edicts are delta encoded.
				id_height = int_seq.pop(0)

				if id_height > 0:
					id_txpos = int_seq.pop(0)
				else:
					id_height = id_height + last_id_height
					id_txpos = last_id_txpos

				last_id_height = id_height
				last_id_txpos = id_txpos

				print(id_height, id_txpos)

				rune_id = f"{id_height}:{id_txpos}"
				
				amount = int_seq.pop(0)
				output = int_seq.pop(0)

				edict = {"id": rune_id, "amount": amount, "output": output}
				runestone['edicts'].append(edict)
				continue

			if tag == 1:
				divisibility = int_seq.pop(0)
				if etching:
					runestone['etching']['divisibility'] = divisibility
				continue

			if tag == 2:
				flags = int_seq.pop(0)

				# The Flag field contains a bitmap of flags, 
				# whose position is 1 << FLAG_VALUE
				etching = flags & (1 << 0) != 0
				terms   = flags & (1 << 1) != 0
				turbo   = flags & (1 << 2) != 0

				# If the value of the flags field after removing recognized flags
				# is nonzero, the runestone is a cenotaph
				cenotaph = flags > 0b111
				assert not cenotaph

				if etching:
					runestone['etching'] = {
					'divisibility': None,
					'premine': None,
					'rune': None,
					'spacers': None,
					'symbol': None,
					'turbo': False
					}

				if etching and terms:
					runestone['etching']['terms'] = {
					'amount': None,
					'cap': None,
					'height': [None, None],
					'offset': [None, None]
					}

				if turbo:
					runestone['turbo'] = True

				continue

			if tag == 3:
				spacers = int_seq.pop(0)
				if etching:
					runestone['etching']['spacers'] = spacers
				continue

			if tag == 4:
				rune_name = decode_name(int_seq.pop(0))
				if etching:
					runestone['etching']['rune'] = rune_name
				continue

			if tag == 5:
				symbol = int_seq.pop(0)
				if etching:
					runestone['etching']['symbol'] = chr(symbol)
				continue

			if tag == 6:
				premine = int_seq.pop(0)
				if etching:
					runestone['etching']['premine'] = premine
				continue

			if tag == 8:
				cap = int_seq.pop(0)
				if etching and terms:
					runestone['etching']['terms']['cap'] = cap
				continue

			if tag == 10:
				amount = int_seq.pop(0)
				if etching and terms:
					runestone['etching']['terms']['amount'] = amount
				continue

			if tag == 12:
				height_start = int_seq.pop(0)
				if etching and terms:
					runestone['etching']['terms']['height'][0] = height_start
				continue

			if tag == 14:
				height_end = int_seq.pop(0)
				if etching and terms:
					runestone['etching']['terms']['height'][1] = height_end
				continue

			if tag == 16:
				offset_start = int_seq.pop(0)
				if etching and terms:
					runestone['etching']['terms']['offset'][0] = offset_start
				continue

			if tag == 18:
				offset_end = int_seq.pop(0)
				if etching and terms:
					runestone['etching']['terms']['offset'][1] = offset_end
				continue

			if tag == 20:
				# The Mint field contains the Rune ID of the rune to be minted
				if mint['id'] == None:
					mint['id'] = int_seq.pop(0)
					continue

				if mint['txpos'] == None:
					mint['txpos'] = int_seq.pop(0)
					runestone['mint'] = f"{mint['id']}:{mint['txpos']}"
					continue

			if tag == 22:
				pointer = int_seq.pop(0)
				runestone['pointer'] = pointer
				continue

		print(dumps(runestone, indent=2, ensure_ascii=False))

if __name__ == "__main__":
	parser = ArgumentParser(description="Parse runestone scripts")
	parser.add_argument("--script", help="bitcoin script", required=True)
	args = parser.parse_args()

	main(args)
