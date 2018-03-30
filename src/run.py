import spacy
from src.objects.ServerInstance import ServerInstance
from src.objects.storyworld.World import World
from src.inputprocessor import infoextraction
from src.dialoguemanager import DialoguePlanner

server = ServerInstance()
worldid = "0"
world = World(worldid)
server.add_world(world)
print("hallo")


#Loading of text and segmentation of sentences
nlp = spacy.load('en_core_web_sm')
document = nlp(infoextraction.reading("document.txt"))
sentences = [sent.string.strip() for sent in document.sents]
list_of_sentences = []
list_of_sent = []
#Character
characters = []

#Part-Of-Speech, NER, Dependency Parsing
for sent in sentences:
    print(sent)
    sent = nlp(sent)
    list_of_sentences.append(infoextraction.pos_ner_nc_processing(sent))

list = []
curr = 0
bef = 0
isFirst = False
# DetailsExtraction
for sent in list_of_sentences:
    if curr == 1 or curr > 1:
        sentences[curr] = infoextraction.coref_resolution(sent, sentences[curr], sentences[bef], world, False)
        print("returned: ", sentences[curr])
    else:
        sentences[curr] = infoextraction.coref_resolution(sent, sentences[curr], sentences[curr], world, True)
        print("returned: ", sentences[curr])

    print("current index: ", curr)
    curr += 1
    if bef == 0 and curr == 1:
        print("oops")
    else:
        bef +=1

print(sentences)
for s in sentences:
    print(s)
    s = nlp(s)
    list_of_sent.append(infoextraction.pos_ner_nc_processing(s))

for s in list_of_sent:
    infoextraction.details_extraction(s, world, "ROOT")
    infoextraction.event_extraction(s, world, "ROOT")

print(world.characters)
print(world.objects)

for c in world.characters:
    print("char", c, type(c))
    print(world.characters[c])
    for a in world.characters[c].attributes:
        print("attr", a.relation, a.name, a.isNegated)

for c in world.objects:
    print("obj", c, type(c))
    print(world.objects[c])
    for a in world.objects[c].attributes:
        print("attr", a.relation, a.name, a.isNegated)

# print("AAAAA")
# for key, values in characters_attributes.items():
#     new_character = Character()
#     new_character.name = key
#     print("CHAR", key)
#     if values is not None:
#         for value in values:
#             print("CHAR ATTR" , value)
#             new_character.attributes.append(value)
#     world.add_character(new_character)
#
# for key, values in object_attributes.items():
#     new_obj = Object()
#     new_obj.name = key
#     print("OBJ", key)
#     if values is not None:
#         for value in values:
#             print("OBJ ATTR", value)
#             new_obj.attributes.append(value)
#     world.add_object(new_obj)

#nlp = StanfordCoreNLP(r'C:\stanford-corenlp-full-2018-01-31', memory='8g')
#props = {'annotators': 'dcoref', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
#output = [nlp.annotate(sent, properties=props) for sent in sentences]
#print("------------------")
#print(output)

#Setting Details
settings = []
time = []

#infoextraction.setting_attribute_extraction(list_of_sentences[0], world)
#Setting Detail Extraction
#infoextraction.setting_attribute_extraction(list_of_sentences, world)


#For Event Extraction
seq_no = []
event_type = []
doer = []
doer_act = []
rec = []
rec_act = []
location = []
event_frame = [seq_no, event_type, doer, doer_act, rec, rec_act, location]

#dialogue
output = DialoguePlanner.retrieve_output("", worldid)
print(output)