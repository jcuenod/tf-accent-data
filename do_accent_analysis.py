import re
from tf.fabric import Fabric
from datetime import datetime

TF = Fabric(locations='/home/jcuenod/Programming/text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('g_word_utf8')
api.makeAvailableIn(globals())

accent_dictionary = {
	"Etnahta": '\u0591',
	"Segol": '\u0592',
	"Shalshelet": '\u0593',
	"Zaqef Qatan": '\u0594',
	"Zaqef Gadol": '\u0595',
	"Tipeha": '\u0596',
	"Revia": '\u0597',
	"Zarqa": '\u0598',
	"Pashta": '\u0599',
	"Yetiv": '\u059A',
	"Tevir": '\u059B',
	"Geresh": '\u059C',
	"Geresh Muqdam": '\u059D',
	"Gershayim": '\u059E',
	"Qarney Para": '\u059F',
	"Telisha Gedola": '\u05A0',
	"Pazer": '\u05A1',
	"Munah": '\u05A3',
	"Mahapakh": '\u05A4',
	"Merkha": '\u05A5',
	"Merkha Kefula": '\u05A6',
	"Darga": '\u05A7',
	"Qadma": '\u05A8',
	"Telisha Qetana": '\u05A9',
	"Yerah Ben Yomo": '\u05AA',
	"Ole": '\u05AB',
	"Iluy": '\u05AC',
	"Dehi": '\u05AD',
	"Zinor": '\u05AE',
	# "HEBREW ACCENT ETNAHTA": '\u0591',
	# "HEBREW ACCENT SEGOL": '\u0592',
	# "HEBREW ACCENT SHALSHELET": '\u0593',
	# "HEBREW ACCENT ZAQEF QATAN": '\u0594',
	# "HEBREW ACCENT ZAQEF GADOL": '\u0595',
	# "HEBREW ACCENT TIPEHA": '\u0596',
	# "HEBREW ACCENT REVIA": '\u0597',
	# "HEBREW ACCENT ZARQA": '\u0598',
	# "HEBREW ACCENT PASHTA": '\u0599',
	# "HEBREW ACCENT YETIV": '\u059A',
	# "HEBREW ACCENT TEVIR": '\u059B',
	# "HEBREW ACCENT GERESH": '\u059C',
	# "HEBREW ACCENT GERESH MUQDAM": '\u059D',
	# "HEBREW ACCENT GERSHAYIM": '\u059E',
	# "HEBREW ACCENT QARNEY PARA": '\u059F',
	# "HEBREW ACCENT TELISHA GEDOLA": '\u05A0',
	# "HEBREW ACCENT PAZER": '\u05A1',
	# "HEBREW ACCENT MUNAH": '\u05A3',
	# "HEBREW ACCENT MAHAPAKH": '\u05A4',
	# "HEBREW ACCENT MERKHA": '\u05A5',
	# "HEBREW ACCENT MERKHA KEFULA": '\u05A6',
	# "HEBREW ACCENT DARGA": '\u05A7',
	# "HEBREW ACCENT QADMA": '\u05A8',
	# "HEBREW ACCENT TELISHA QETANA": '\u05A9',
	# "HEBREW ACCENT YERAH BEN YOMO": '\u05AA',
	# "HEBREW ACCENT OLE": '\u05AB',
	# "HEBREW ACCENT ILUY": '\u05AC',
	# "HEBREW ACCENT DEHI": '\u05AD',
	# "HEBREW ACCENT ZINOR": '\u05AE',

	# Some of these may actually still be useful:
	# Maqaf, sof pasuq

	# "HEBREW MARK MASORA CIRCLE": '\u05AF',
	# "HEBREW POINT SHEVA": '\u05B0',
	# "HEBREW POINT HATAF SEGOL": '\u05B1',
	# "HEBREW POINT HATAF PATAH": '\u05B2',
	# "HEBREW POINT HATAF QAMATS": '\u05B3',
	# "HEBREW POINT HIRIQ": '\u05B4',
	# "HEBREW POINT TSERE": '\u05B5',
	# "HEBREW POINT SEGOL": '\u05B6',
	# "HEBREW POINT PATAH": '\u05B7',
	# "HEBREW POINT QAMATS": '\u05B8',
	# "HEBREW POINT HOLAM": '\u05B9',
	# "HEBREW POINT QUBUTS": '\u05BB',
	# "HEBREW POINT DAGESH OR MAPIQ (or shuruq)": '\u05BC',
	# "HEBREW POINT METEG": '\u05BD',
	# "HEBREW PUNCTUATION MAQAF": '\u05BE',
	# "HEBREW POINT RAFE": '\u05BF',
	# "HEBREW PUNCTUATION PASEQ": '\u05C0',
	# "HEBREW POINT SHIN DOT": '\u05C1',
	# "HEBREW POINT SIN DOT": '\u05C2',
	# "HEBREW PUNCTUATION SOF PASUQ": '\u05C3',
	# "HEBREW MARK UPPER DOT": '\u05C4',
	# "HEBREW PUNCTUATION GERESH": '\u05F3',
	# "HEBREW PUNCTUATION GERSHAYIM": '\u05F4'
}

def which_match(word):
	ret = []
	for k, v in accent_dictionary.items():
		if re.search(v, word):
			ret.append(k)
	return ret

print("Beginning nodes accent loop:")
counter = 0
node_data = []
for n in F.otype.s('word'):
	word = F.g_word_utf8.v(n)
	if re.search('[' + "".join(list(accent_dictionary.values())) + ']', word):
		node_data.append({
			'node': n,
			'word': word,
			'accent': which_match(word),
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
