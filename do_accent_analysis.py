import re
from tf.fabric import Fabric
from datetime import datetime
import unicodedata
from AccentCatalog import dataFromAccentCombo

TF = Fabric(locations='../../text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('g_word_utf8 trailer_utf8')
api.makeAvailableIn(globals())

# 0591-05AE	= normal accents
# 05C0		= paseq
# 05BE		= Maqqef
# 05BD		= Meteg
# 05C3		= Sof Pasuq
unicode_accent_range = '[\u0591-\u05AE\u05C0\u05BE\u05BD\u05C3]'

def normalisedUnicodeNameFromCharacter(character):
	return re.sub(r'HEBREW (ACCENT|PUNCTUATION|POINT) ', "", unicodedata.name(character)).title()

composite_list = []
def whichMatch(word, ref_tuple):
	accent_matches = re.findall(unicode_accent_range, word)
	accent_data = dataFromAccentCombo("".join(accent_matches), ref_tuple)
	if not accent_data:
		ret = {
			"name": "[" + ", ".join(list(map(lambda x: normalisedUnicodeNameFromCharacter(x), accent_matches))) + "]",
			"quality": "unknown"
		}
	else:
		ret = {
			"name": accent_data["name"],
			"quality": accent_data["type"]
		}
	return ret

print("\nBeginning nodes accent loop:")
counter = 0
node_data = []
# composites_list = {}
for n in F.otype.s('word'):
	word = F.g_word_utf8.v(n) + F.trailer_utf8.v(n)
	if re.search(unicode_accent_range, word):
		this_accent = whichMatch(word, T.sectionFromNode(n))
		this_ref = T.sectionFromNode(n)
		node_data.append({
			'node': n,
			'word': word,
			'accent': this_accent["name"],
			'quality': this_accent["quality"],
			'ref': this_ref
		})
		# if len(this_accent) > 1:
		# 	if str_this_accent not in composites_list:
		# 		composites_list[str_this_accent] = { "counter": 0, "refs": [] }
		# 	composites_list[str_this_accent]["counter"] += 1
		# 	composites_list[str_this_accent]["refs"].append("{} {}:{}".format(*this_ref))
	else:
		node_data.append({
			'node': n,
			'word': word,
			'accent': "",
			'quality': "",
			'ref': T.sectionFromNode(n)
		})
	counter += 1
	if counter % 50000 == 0:
		print(" |", counter)
print(" -", counter)
print("Complete\n")

tf_accent_filename = "accents.tf"
tf_accent_fileheader = '''@node
@valueType=str
@writtenBy=James Cuénod & ETCBC4c
@dateWritten={0}

'''.format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
print("writing file:", tf_accent_filename)

with open(tf_accent_filename, mode='wt', encoding='utf-8') as out:
	out.write(tf_accent_fileheader)
	out.write('\n'.join(map(lambda x: x['accent'], node_data)))


tf_accent_quality_filename = "accent_quality.tf"
tf_accent_quality_fileheader = '''@node
@valueType=str
@writtenBy=James Cuénod & ETCBC4c
@dateWritten={0}

'''.format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
print("writing file:", tf_accent_quality_filename)

with open(tf_accent_quality_filename, mode='wt', encoding='utf-8') as out:
	out.write(tf_accent_quality_fileheader)
	out.write('\n'.join(map(lambda x: x['quality'], node_data)))

# composite_accent_log_filename = 'composite_accents.log'
# print("writing file:", composite_accent_log_filename)
# with open(composite_accent_log_filename, mode='wt', encoding='utf-8') as out:
# 	sorted_list = list(sorted(composites_list, key=lambda k: composites_list[k]['counter'], reverse=True))
# 	for k in sorted_list:
# 		v = composites_list[k]
# 		out.write("\n" + k + ": " + str(v["counter"]))
# 		if v["counter"] < 50:
# 			out.write("\n" + ", ".join(v["refs"]))
# 		out.write("\n")
