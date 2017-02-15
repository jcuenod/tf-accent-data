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
	"Legarmeh": ['Mahapakh', 'Paseq']
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
for n in F.otype.s('word'):
	word = F.g_word_utf8.v(n) + F.trailer_utf8.v(n)
	if re.search(unicode_accent_range, word):
		node_data.append({
			'node': n,
			'word': word,
			'accent': whichMatch(word),
			'ref': T.sectionFromNode(n)
		})
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
print("Complete\n\n")

print("List of composites found:\n--\n\t","\n\t".join(list(set(map(lambda x: ", ".join(x), composite_list)))))

print("")
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
