import re
from tf.fabric import Fabric
from datetime import datetime
import unicodedata
from AccentCatalog import dataFromAccentCombo

TF = Fabric(locations=['../../text-fabric-data', '.'], modules='hebrew/etcbc4c')
api = TF.load('g_word_utf8 trailer_utf8')
api.makeAvailableIn(globals())

# 0591-05AE	= normal accents
# 05C0		= paseq
# 05BE		= Maqqef # removed (with maqqef 1894 missed accents, without: 1491)
# 05BD		= Meteg
# 05C3		= Sof Pasuq
unicode_accent_range = '[\u0591-\u05AE\u05BE\u05C0\u05BD\u05C3]'

def normalisedUnicodeNameFromCharacter(character):
	return re.sub(r'HEBREW (ACCENT|PUNCTUATION|POINT) ', "", unicodedata.name(character)).title()

accent_coverage_counter = {
	"missed": 0,
	"decalogue": 0,
	"gen3522": 0,
	"hit": 0,
}
failures = []
composite_list = []
def whichMatch(word, ref_tuple):
	global accent_coverage_counter
	global failures
	accent_matches = re.findall(unicode_accent_range, word)
	accent_data = dataFromAccentCombo("".join(accent_matches), ref_tuple)
	if not accent_data:
		accent_repr = "[" + ", ".join(list(map(lambda x: normalisedUnicodeNameFromCharacter(x), accent_matches))) + "]"
		if ref_tuple == ("Genesis", 35, 22):
			accent_coverage_counter["gen3522"] += 1
			accent_repr = "double tradition: " + ", ".join(list(map(lambda x: normalisedUnicodeNameFromCharacter(x), accent_matches)))
		elif (ref_tuple[0] == "Exodus" and ref_tuple[1] == 20) or (ref_tuple[0] == "Deuteronomy" and ref_tuple[1] == 5):
			accent_coverage_counter["decalogue"] += 1
			accent_repr = "double tradition: " + ", ".join(list(map(lambda x: normalisedUnicodeNameFromCharacter(x), accent_matches)))
		else:
			failures.append(str(ref_tuple) + " " + accent_repr)
			accent_coverage_counter["missed"] += 1
		ret = {
			"name": accent_repr,
			"quality": "unknown"
		}
	else:
		ret = {
			"name": accent_data["name"],
			"quality": accent_data["type"]
		}
		accent_coverage_counter["hit"] += 1
	return ret


counter = 0
def getNodeDataFromWord(word, n):
	global counter
	counter += 1
	if counter % 50000 == 0:
		print(" |", counter)

	w = word
	word = w.strip()
	if re.search("(\s|\u05BE)", word):
		word = re.sub(".*[\s\u05BE](.*)$","\\1", word)

	if re.search(unicode_accent_range, word):
		this_accent = whichMatch(word, T.sectionFromNode(n))
		this_ref = T.sectionFromNode(n)
		node_data = {
			'accent': this_accent["name"],
			'quality': this_accent["quality"],
		}
		return node_data
	else:
		node_data = {
			'accent': "",
			'quality': "",
		}
		return node_data



print("\nFinding accent units:")
gigantic_node_accent_dictionary = {
	"accent": {},
	"accent_quality": {},
}
glue = {'', '־'}
node2au = []
current_au = ""
current_au_nodes = []
for w in F.otype.s('word'):
	trailer = F.trailer_utf8.v(w)
	current_au += F.g_word_utf8.v(w) + trailer
	current_au_nodes.append(w)
	if trailer not in glue:
		n = current_au_nodes[-1]
		nodedata = getNodeDataFromWord(current_au, n)
		current_au = ""
		current_au_nodes = []
		if nodedata == None:
			continue
		gigantic_node_accent_dictionary["accent"][n] = nodedata["accent"]
		gigantic_node_accent_dictionary["accent_quality"][n] = nodedata["quality"]
if current_au:
	nodedata = getNodeDataFromWord(current_au, current_au_nodes[-1])
	if nodedata != None:
		gigantic_node_accent_dictionary["accent"][current_au_nodes[-1]] = nodedata["accent"]
		gigantic_node_accent_dictionary["accent_quality"][current_au_nodes[-1]] = nodedata["quality"]

print(" -", counter)
print("Complete\n")

print('Assembled {} accented units'.format(len(gigantic_node_accent_dictionary.keys())))

print("\n".join(failures), "\n")

print("Accents missed:")
print(accent_coverage_counter, "\n")
#{'missed': 224, 'decalogue': 104, 'gen3522': 3, 'hit': 268579}
#{'missed': 179, 'decalogue': 100, 'gen3522': 3, 'hit': 265469}
#{'missed': 108, 'decalogue': 100, 'gen3522': 3, 'hit': 257868}

feature_metadata = {
	"accent":         {"valueType": "str", "author": "James Cuénod"},
	"accent_quality": {"valueType": "str", "author": "James Cuénod"}
}
TF.save(nodeFeatures=gigantic_node_accent_dictionary, metaData=feature_metadata, module='accent-data')
