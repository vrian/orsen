from numpy import random
from src.objects.ServerInstance import ServerInstance
from src.inputprocessor.infoextraction import getCategory, CAT_STORY, CAT_COMMAND, CAT_ANSWER
from src.dialoguemanager import DBO_Move, Move
from src.db.concepts import DBO_Concept
from src.objects.eventchain.EventFrame import EventFrame, FRAME_EVENT, FRAME_DESCRIPTIVE

from src.objects.storyworld.Character import Character
from src.objects.storyworld.Object import Object
from src.objects.storyworld.World import World
import time
import spacy

MOVE_FEEDBACK = 1
MOVE_GENERAL_PUMP = 2
MOVE_SPECIFIC_PUMP = 3
MOVE_HINT = 4
MOVE_REQUESTION = 5
MOVE_UNKNOWN = 6

CONVERT_INFINITIVE = "inf"
CONVERT_1PRSG = "1sg"
CONVERT_2PRSG = "2sg"
CONVERT_3PRSG = "3sg"
CONVERT_PRPL = "pl"
CONVERT_PRPART = "part"

CONVERT_PAST = "p"
CONVERT_1PASG = "1sgp"
CONVERT_2PASG = "2sgp"
CONVERT_3PASG = "3sgp"
CONVERT_PAPL = "ppl"
CONVERT_PAPART = "ppart"

server = ServerInstance()
nlp = spacy.load('en_core_web_sm')

def retrieve_output(coreferenced_text, world_id):
    world = server.worlds[world_id]
	
    extract_information(coreferenced_text)
	
    if len(world.reponses) > 0:
        last_response_type_num = world.reponses[len(world.reponses)-1].type_num
    else:
        last_response_type_num = -1
    output = ""
    choice = -1
    if coreferenced_text == "":  # if no input found
        world.empty_response += 1

        if world.empty_response == 1:
            if last_response_type_num in [MOVE_FEEDBACK, MOVE_HINT]:
                output = Move.Move(template=["I'm sorry, I did not understand what you just said. Can you say it again?"], type_num=MOVE_REQUESTION)
            elif last_response_type_num == MOVE_GENERAL_PUMP:
                output = generate_response(MOVE_SPECIFIC_PUMP, world)
            elif last_response_type_num == MOVE_SPECIFIC_PUMP:
                output = generate_response(MOVE_HINT, world)
                output.template = ["What if "]+output.template
            else:
                output = Move.Move(template=["I don't think I heard you. Can you say that last part again?"], type_num=MOVE_REQUESTION)

        if world.empty_response == 2:
            print("2nd no response")
            if last_response_type_num == MOVE_GENERAL_PUMP:
                output = generate_response(MOVE_SPECIFIC_PUMP, world)
            elif last_response_type_num == MOVE_SPECIFIC_PUMP:
                output = generate_response(MOVE_HINT, world)
                output.template = ["What if "] + output.template
            else:
                choice = random.randint(MOVE_GENERAL_PUMP, MOVE_HINT+1)
                output = generate_response(choice, world)

        elif world.empty_response == 3:
            print("3rd no response")
            choice = MOVE_REQUESTION
            output = Move.Move(template=["I don't think I can hear you, are you sure you want to continue?"], type_num=choice)
    else:

        world.empty_response = 0

        if getCategory(coreferenced_text) == CAT_STORY:
            choice = random.randint(MOVE_FEEDBACK, MOVE_HINT+1)
            output = generate_response(choice, world)

        elif getCategory(coreferenced_text) == CAT_ANSWER:
            print("check_answer")
            # TEMP TODO: idk how to answer this lmao / if "yes" or whatever, add to character data
            if last_response_type_num == MOVE_REQUESTION:
                output = Move.Move(template=["Ok, let's keep going then!"], type_num=MOVE_UNKNOWN)
            else:
                choice = random.randint(MOVE_FEEDBACK, MOVE_HINT+1)
                output = generate_response(choice, world)

        elif getCategory(coreferenced_text) == CAT_COMMAND:
            # TEMP TODO: check for further commands
            choice = random.randint(MOVE_FEEDBACK, MOVE_HINT+1)

            if "your turn" in coreferenced_text:
                choice = MOVE_HINT
            elif "what" in coreferenced_text \
                    and ("say" in coreferenced_text or "next" in coreferenced_text):
                choice = random.randint(MOVE_GENERAL_PUMP, MOVE_SPECIFIC_PUMP+1)

            output = generate_response(choice, world)

        else:
            output = Move.Move(template=["I don't know what to say."], type_num=MOVE_UNKNOWN)

    world.reponses.append(output)

    return output

def extract_information(text):
		
	document = nlp(text)
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



def generate_response(move_code, world, remove_index=[]):
    choices = []

    subject = None
    if len(world.reponses) > 0:
        last_response_id = world.reponses[len(world.reponses)-1].move_id
    else:
        last_response_id = -1

    if move_code == MOVE_FEEDBACK:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_FEEDBACK)

    elif move_code == MOVE_GENERAL_PUMP:
        pre_choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_GENERAL_PUMP)

        if len(world.event_chain) > 0:
            last = world.event_chain[len(world.event_chain)-1]
            for item in pre_choices:
                if last.event_type == FRAME_EVENT and "happen" in item.get_string_response():
                    choices.append(item)
                if "happen" not in item.get_string_response():
                    choices.append(item)
        else:
            choices = pre_choices

    elif move_code == MOVE_SPECIFIC_PUMP:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_SPECIFIC_PUMP)

    elif move_code == MOVE_HINT:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_HINT)

    elif move_code == MOVE_REQUESTION:
        # TODO: requestioning decisions to be made
        choices = ["requestioning..."]

    index_loop = 0
    while True:
        index_loop += 1
        index = random.randint(0, len(choices))
        move = choices[index]

        if move.move_id != last_response_id and move.move_id not in remove_index:
            move.type_num = move_code
            break

        if index_loop > 20:
            return generate_response(MOVE_FEEDBACK, world)

    for blank_type in move.blanks:

        if ":" in blank_type:
            split_relation = str(blank_type).split(":")
            relation_index = -1
            replacement_index = -1

            for i in range(0, len(split_relation)):
                if split_relation[i] in DBO_Concept.RELATIONS:
                    relation_index = i
                else:
                    replacement_index = i

            usable_concepts = []
            txt_relation = split_relation[relation_index]
            to_replace = split_relation[replacement_index]

            if to_replace in ["setting"]:
                if to_replace == "setting":
                    if subject is None:
                        remove_index.append(move.move_id)
                        return generate_response(move_code, world, remove_index)
                    elif subject.inSetting is None:
                        remove_index.append(move.move_id)
                        return generate_response(move_code, world, remove_index)
                    else:
                        txt_concept = subject.inSetting.name

            else:
                txt_concept = to_replace

            if relation_index == 0:
                usable_concepts = DBO_Concept.get_concept_like(txt_relation, second=txt_concept)
            elif relation_index == 1:
                usable_concepts = DBO_Concept.get_concept_like(txt_relation, first=txt_concept)
            else:
                print("ERROR: Index not found.")

            if len(usable_concepts) > 0 :
                concept_string = ""
                concept_index = random.randint(0,len(usable_concepts))

                if relation_index == 0:
                    concept_string = usable_concepts[concept_index].first
                elif relation_index == 1:
                    concept_string = usable_concepts[concept_index].second

                move.template[move.template.index(to_replace)] = concept_string

        elif blank_type in DBO_Concept.RELATIONS:

            # CHOOSE THE CONCEPT
            decided_concept = ""
            decided_node = -1

            charas = world.get_top_characters()
            objects = world.get_top_objects()
            list_choices = charas + objects
            loop_total = 0

            while True and subject is None:

                if len(list_choices) > 0:
                    loop_total += 1
                    choice_index = random.randint(0, len(list_choices))
                    decided_item = list_choices[choice_index]
                else:
                    break

                if isinstance(decided_item, Object):
                    decided_concept = decided_item.name
                    subject = decided_item
                    decided_node = 0

                elif isinstance(decided_item, Character):
                    # get... something... relationship??
                    # TODO: use relationship or something to get a concept
                    print("check relationship")

                if decided_node != -1 or loop_total > 10:
                    break

            # find
            if decided_node == 0:
                usable_concepts = DBO_Concept.get_concept_like(blank_type, first=decided_concept)
            elif decided_node == 1:
                usable_concepts = DBO_Concept.get_concept_like(blank_type, second=decided_concept)

            if len(usable_concepts) == 0:
                usable_concepts = DBO_Concept.get_concept_like(blank_type)

            loop_total = 0
            while len(usable_concepts) > 0:
                loop_total += 1
                usable_concepts = DBO_Concept.get_concept_like(blank_type)
                if loop_total > 10:
                    break

            if len(usable_concepts) > 0:
                concept_index = random.randint(0,len(usable_concepts))
                concept = usable_concepts[concept_index]
                move.template[move.template.index("start")] = concept.first
                move.template[move.template.index("end")] = concept.second
            else:
                print("ERROR: NO USABLE CONCEPTS decided:",decided_concept)

        elif blank_type == "Object":

            if subject is None:
                charas = world.get_top_characters()
                objects = world.get_top_objects()
                list_choices = charas + objects

                choice_index = random.randint(0, len(choices))
                subject = list_choices[choice_index]

            move.template[move.template.index("object")] = subject.id

        elif blank_type == "Item":

            if subject is None:
                objects = world.get_top_objects()

                choice_index = random.randint(0, len(choices))
                subject = objects [choice_index]

            move.template[move.template.index("item")] = subject.id

        elif blank_type == "Character":
            if subject is None or not isinstance(subject, Character):
                charas = world.get_top_characters(5)

                if len(charas) > 0:
                    choice_index = random.randint(0, len(charas))
                    subject = charas[choice_index]
                else:
                    remove_index.append(move.move_id)
                    return generate_response(move_code, world, remove_index)
            else:
                chara = subject

            move.template[move.template.index("character")] = subject.id

        elif blank_type == "inSetting":
            if subject is None:
                remove_index.append(move.move_id)
                return generate_response(move_code, world,remove_index)
            elif subject.inSetting is None:
                remove_index.append(move.move_id)
                return generate_response(move_code, world,remove_index)
            else:
                move.template[move.template.index("setting")] = subject.inSetting.name

        elif blank_type == "Repeat":
            if len(world.event_chain) > 0:
                move.template[move.template.index("repeat")]\
                    = world.event_chain[len(world.event_chain)-1].to_sentence_string()
            else:
                remove_index.append(move.move_id)
                return generate_response(move_code, world,remove_index)
        elif blank_type == "Event":
            print("replace event")
            # TODO: event verb replacements

    move.subject = subject
    return move


# start_time = time.time()
#
# test_world = World()
# server.worlds[test_world.id] = test_world
#
# test_world.characters["KAT"] = Character("KAT", "KAT", times=3)
# test_world.characters["DAVE"] = Character("DAVE", "DAVE", times=5)
# test_world.characters["JADE"] = Character("JADE", "JADE", times=0)
# test_world.characters["ROSE"] = Character("ROSE", "ROSE", times=0)
#
# test_world.objects["bag"] = Object("bag", "bag", times=3)
# test_world.objects["book"] = Object("book", "book", times=5)
# test_world.objects["pen"] = Object("pen", "pen", times=0)
#
# print(retrieve_output("Whatever.", test_world.id))
# print(retrieve_output("Whatever.", test_world.id))
# print(retrieve_output("Whatever.", test_world.id))
# print(retrieve_output("Whatever.", test_world.id))
#
# print(retrieve_output("Whatever.", test_world.id))
# print(retrieve_output("Whatever.", test_world.id))
# print(retrieve_output("Whatever.", test_world.id))
# print(retrieve_output("Whatever.", test_world.id))
#
# print("--- %s seconds ---" % (time.time() - start_time))
