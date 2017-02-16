import re
from tf.fabric import Fabric
from datetime import datetime
import unicodedata

TF = Fabric(locations='../../text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('g_word_utf8 trailer_utf8')
api.makeAvailableIn(globals())

# 0591-05AE	= normal accents
# 05C0		= paseq
unicode_accent_range = '[\u0591-\u05AE\u05C0]'

composite_accents = {
	"Shene Pashtim": ["Qadma", "Pashta"],
	"Mahapakh Legarmeh": ['Mahapakh', 'Paseq'],
	"Legarmeh": ['Munah', 'Paseq']
}
composite_accent_values = list(composite_accents.values())

def normalisedUnicodeNameFromCharacter(character):
	return re.sub(r'HEBREW (ACCENT|PUNCTUATION) ', "", unicodedata.name(character)).title()

composite_list = []
def whichMatch(word):
	accent_matches = re.findall(unicode_accent_range, word)
	ret = list(map(lambda x: normalisedUnicodeNameFromCharacter(x), accent_matches))
	if len(ret) > 1:
		composite_list.append(ret)
	if ret in composite_accent_values:
		newret = list(composite_accents.keys())[composite_accent_values.index(ret)]
		ret = [newret]
	return ret

print("\nBeginning nodes accent loop:")
counter = 0
node_data = []
composites_list = {}
for n in F.otype.s('word'):
	word = F.g_word_utf8.v(n) + F.trailer_utf8.v(n)
	if re.search(unicode_accent_range, word):
		this_accent = whichMatch(word)
		str_this_accent = ", ".join(this_accent)
		this_ref = T.sectionFromNode(n)
		node_data.append({
			'node': n,
			'word': word,
			'accent': str_this_accent,
			'ref': this_ref
		})
		if len(this_accent) > 1:
			if str_this_accent not in composites_list:
				composites_list[str_this_accent] = { "counter": 0, "refs": [] }
			composites_list[str_this_accent]["counter"] += 1
			composites_list[str_this_accent]["refs"].append("{} {}:{}".format(*this_ref))
	else:
		node_data.append({
			'node': n,
			'word': word,
			'accent': [],
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
	out.write('\n'.join(map(lambda x: ", ".join(x['accent']), node_data)))

composite_accent_log_filename = 'composite_accents.log'
print("writing file:", composite_accent_log_filename)
with open(composite_accent_log_filename, mode='wt', encoding='utf-8') as out:
	sorted_list = list(sorted(composites_list, key=lambda k: composites_list[k]['counter'], reverse=True))
	for k in sorted_list:
		v = composites_list[k]
		out.write("\n" + k + ": " + str(v["counter"]))
		if v["counter"] < 50:
			out.write("\n" + ", ".join(v["refs"]))
		out.write("\n")
