from src.db.concepts import DBO_Concept
from src.objects.eventchain.EventFrame import EventFrame, FRAME_DESCRIPTIVE, FRAME_EVENT
from src.objects.nlp.Sentence import Sentence
from src.objects.storyworld.Attribute import Attribute
from src.objects.storyworld.Character import Character
from src.objects.storyworld.Object import Object
from src.objects.storyworld.Setting import Setting
from neuralcoref import Coref
import _operator
# ----- luisa


def reading(filename):
    with open(filename, 'r') as f:
        userinput = f.read()
    return userinput


def pos_ner_nc_processing(sentence):
    new_sentence = Sentence()
    new_sentence.words = sentence
    for token in sentence:
        new_sentence.children.append([])
        #print("---POS----");
        #print(token.text, token.head.text, token.lemma_, token.pos_, token.tag_, token.dep_)
        new_sentence.text_token.append(token.text)
        new_sentence.head_text.append(token.head.text)
        new_sentence.lemma.append(token.lemma_)
        new_sentence.pos.append(token.pos_)
        new_sentence.tag.append(token.tag_)
        new_sentence.dep.append(token.dep_)

        new_sentence.finished_nodes.append(0)
        for child in token.children:
            # print("child", child)
            new_sentence.children[len(new_sentence.children)-1].append(child)

    for ent in sentence.ents:
         # print("---NER---")
         # print(ent.text, ent.start_char, ent.end_char, ent.label_)
         new_sentence.text_ent.append(ent.text)
         new_sentence.label.append(ent.label_)

    for chunk in sentence.noun_chunks:
        # print("---NC---")
        # print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)

        new_sentence.text_chunk.append(chunk.text)
        new_sentence.dep_root.append(chunk.root.dep_)
        new_sentence.dep_root_head.append(chunk.root.head.text)

    return new_sentence


def find_text_index(sent, child):
    num = 0
    child = str(child).lower()
    temp = child.split()
    for k in range(0, len(sent.text_token)):
        text_token = str(sent.text_token[k]).lower()
        if (temp[-1] == text_token) and (sent.finished_nodes[k] == 0):
            num = k
            break
    return num


def find_ent_index(sent, ent):
    ent = ent.lower()
    for k in range(0, len(sent.text_ent)):
        if ent in str(sent.text_ent[k]).lower():
            return k
            break
    return None


def details_extraction(sent, world, current_node, subj="", neg=""):
    num = -1
    subject = subj
    current_index = -1
    dative = ""
    direct_object = ""
    for i in range(0, len(sent.dep)):
        if (sent.dep[i] == current_node) and (sent.finished_nodes[i] == 0):
            current_index = i
            sent.finished_nodes[i] = 1
            break

    if neg =="":
        is_negated = False
    else:
        is_negated = neg

    if current_index != -1:
        i = current_index
        for j in range(0, len(sent.children[i])):
            num = find_text_index(sent, str(sent.children[i][j]))
            if num != -1 and sent.finished_nodes[num] == 0 and\
                    sent.dep[num] in ["nsubj", "acomp", "attr", "nsubjpass", "dobj", "xcomp", "appos", "relcl",
                                      "npadvmod", "advmod", "pcomp"]:
                print("CHILD", sent.dep[num])
                # nominal subject
                if sent.dep[num] == "nsubj":
                    subject = compound_extraction(sent, str(sent.children[i][j]))
                    add_objects(sent, str(subject), sent.dep[num], sent.lemma[i], world)
                    add_capability(sent, str(sent.lemma[i]), str(subject), world, current_index)

                # nominal subject (passive) or direct object
                elif sent.dep[num] == "nsubjpass" or sent.dep[num] == "dobj":
                    if not subject:
                        subject = compound_extraction(sent, str(sent.children[i][j]))

                    if dative and sent.dep[num] == "dobj":
                        subject = compound_extraction(sent, str(sent.children[i][j]))
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, dative)
                    else:
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world)

                    if sent.dep[num] == "dobj":
                        direct_object = sent.text_token[num]

                # adjectival complement
                elif sent.dep[num] == "acomp":
                    add_attributes(sent, str(sent.children[i][j]), str(subject), world, is_negated)
                    is_negated = False

                # attribute and appositional modifier
                elif sent.dep[num] == "attr":
                    if not add_settings(sent, num, subject, is_negated, world):
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, subject)
                        if not subject:
                            subject = sent.text_token[num]

                    is_negated = False

                # appositional modifier
                elif sent.dep[num] == "appos":
                    if not add_settings(sent, num, subject, is_negated, world):
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, compound_extraction(sent, str(sent.head_text[num])))

                    is_negated = False

                # open clausal compliment
                elif sent.dep[num] in ["xcomp", "pcomp"]:
                    print("ENTERING", sent.finished_nodes[num])
                    add_capability(sent, str(sent.lemma[num]), str(subject), world, num)
                    is_negated = False

                # relative clause modifier
                elif sent.dep[num] == "relcl":
                    add_capability(sent, str(sent.lemma[num]), str(sent.head_text[num]), world, num)

                # noun phrase as adverbial modifier
                elif num != -1 and sent.dep[num] in ["npadvmod", "advmod"]:
                    add_settings(sent, num, subject, is_negated, world)
                    sent.finished_nodes[num] = 1

                if sent.children[num] is not None:
                    for c in sent.children[num]:
                        dep_index = find_text_index(sent, str(c))
                        if sent.finished_nodes[dep_index] == 0:
                            details_extraction(sent, world, sent.dep[num], subject, is_negated)

                sent.finished_nodes[num] = 1

            # object predicate
            elif num != -1 and sent.dep[num] == "oprd":
                if direct_object:
                    add_attributes(sent, sent.text_token[num], direct_object, world)
                else:
                    add_attributes(sent, sent.text_token[num], subject, world)

            # negation
            elif num != -1 and sent.dep[num] == "neg":
                sent.finished_nodes[num] = 1
                is_negated = True

            # object of preposition
            elif num != -1 and sent.dep[num] == "pobj":
                if not add_settings(sent, num, subject, is_negated, world):
                    add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num], sent.lemma[i]
                                , world)
                details_extraction(sent, world, sent.dep[num], subject, is_negated)
                sent.finished_nodes[num] = 1

            # dative - the noun to which something is given
            elif num != -1 and sent.dep[num] == "dative":
                if str(sent.text_token[num]) == "to":
                    details_extraction(sent, world, sent.dep[num], subject, is_negated)
                    if sent.children[num]:
                        dative = compound_extraction(sent, sent.children[num][0])
                else:
                    add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num], sent.lemma[i],
                                world)
                    dative = compound_extraction(sent, str(sent.children[i][j]))

                sent.finished_nodes[num] = 1

            elif num != -1 and sent.dep[num] == "agent":
                for nc in range(0, len(sent.text_chunk)):
                    if sent.dep_root_head[nc] == sent.text_token[num]:
                        add_objects(sent, compound_extraction(sent, str(sent.text_chunk[nc])), sent.dep[num],
                                    sent.lemma[i], world)
                        add_capability(sent, str(sent.lemma[i]), str(sent.text_chunk[nc]), world, current_index)
                        sent.finished_nodes[num] == 1
                        break

            # adverbial clause modifier
            # clausal complement
            # conjunction
            # preposition
            # agent
            # adverbial modifier
            elif num != -1 \
                    and sent.dep[num] in ["advcl","ccomp", "conj", "prep", "acl"]:
                details_extraction(sent, world, sent.dep[num], subject, is_negated)

            else:
                print("WARNING: Dependecy ", sent.dep[num],  " not included in the list")
    else:
        print("ERROR: Cannot find current index or node ", current_node,  " has been recorded")


def compound_extraction(sent, subj):
    num = 0
    subj = str(subj).lower()
    temp = subj.split()

    if not temp:
        return ""

    for k in range(0, len(sent.text_token)):
        text_token = str(sent.text_token[k]).lower()
        if str(temp[-1]) == text_token:
            num = k
            break

    for c in sent.children[num]:
        c = str(c).lower()

        for k in range(0, len(sent.text_token)):
            text_token = str(sent.text_token[k]).lower()
            if text_token == c:
                num = k
                break

        if sent.dep[num] == "compound":
            sent.finished_nodes[num] = 1
            return str(sent.text_token[num]).lower() + " " + subj

    return subj


def char_conj_extractions(sent, subj):
    subj = str(subj).lower()
    list_of_conj = [subj]
    temp = str(subj).split()
    if not temp:
        return []

    subj = temp[-1]
    for k in range(0, len(sent.head_text)):
        head_text = str(sent.head_text[k]).lower()
        if head_text == subj and sent.dep[k] == "conj":
            subj = sent.text_token[k].lower()
            list_of_conj.append(compound_extraction(sent, subj))
            sent.finished_nodes[k] = 1
    return list_of_conj


def add_capability(sent, attr, subject, world, num):
    list_of_char = char_conj_extractions(sent, subject)
    list_of_capabilities = [attr.lower()]
    head = attr.lower()

    for i in range(0, len(sent.words)):
        if sent.dep[i] in ['conj'] and (sent.head_text[i] == str(head)):
            list_of_capabilities.append(sent.text_token[i].lower())
            head = sent.text_token[i].lower()

    if sent.dep[num-1] == "neg":
        negation = True
    else:
        negation = False
    for cap in list_of_capabilities:
        if cap not in ["is", "was", "are", "be", "am", "are", "were", "been", "being"]:

            if sent.dep[num] == "relcl":
                new_attribute = Attribute(DBO_Concept.RECEIVED_ACTION, cap, negation)
            else:
                new_attribute = Attribute(DBO_Concept.CAPABLE_OF, cap, negation)
            for c in list_of_char:
                c = str(c).lower()
                if c in world.characters:
                    new_attribute = check_duplicate_attribute(world.characters[c].attributes, new_attribute)
                    if new_attribute is not None:
                        world.characters[c].attributes.append(new_attribute)
                elif c in world.objects:
                    new_attribute = check_duplicate_attribute(world.objects[c].attributes, new_attribute)
                    if new_attribute is not None:
                        world.objects[c].attributes.append(new_attribute)


def add_objects(sent, child, dep, lemma, world, subject=""):
    list_of_char = char_conj_extractions(sent, child)
    for c in list_of_char:
        c = c.lower()
        if (c not in world.characters) and (c not in world.objects):
            if (DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) or
                    DBO_Concept.get_concept_specified("person", DBO_Concept.CAPABLE_OF, lemma) is not None)\
                    and dep in ["nsubj", "agent"]:
                new_character = Character()
                new_character.name = c
                new_character.id = c
                new_character.attributes = []
                new_character.type = []
                new_character.inSetting = {'LOC': None, 'DATE': None, 'TIME': None}
                if sent.location:
                    new_character.inSetting = sent.location
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned = 1
                print("ADDED", new_character.name)

            else:
                new_object = Object()
                new_object.name = c
                new_object.id = c
                new_object.attributes = []
                new_object.type = []
                new_object.inSetting = {'LOC': None, 'DATE': None, 'TIME': None}
                if sent.location:
                    new_object.inSetting = sent.location
                world.add_object(new_object)
                world.objects[new_object.id].timesMentioned = 1
                print("ADDED", new_object.name)

        elif c in world.objects:
            if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None \
                    and dep == "nsubj":
                new_character = Character.convert_from_object(world.objects[c])
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned += 1
            else:
                world.objects[c].timesMentioned += 1

        elif c in world.settings:
            if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None \
                    and dep == "nsubj":
                new_character = Character.convert_from_setting(c)
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned += 1

        elif c in world.characters:
            world.characters[c].timesMentioned += 1

        # add amod and poss attribute
        char_index = find_text_index(sent, c)
        for ch in sent.children[char_index]:
            index = find_text_index(sent, ch)

            if sent.dep[index] in ["amod", "nummod"]:
                add_attributes(sent, sent.text_token[index], str(c), world)
                sent.finished_nodes[index] = 1

            elif sent.dep[index] in ["poss"]:
                if sent.text_token[index] in world.characters:
                    add_attributes(sent, c, sent.text_token[index], world, "", DBO_Concept.HAS)
                    char = world.characters[sent.text_token[index]]
                    char.timesMentioned += 1
                    sent.finished_nodes[index] = 1
                elif sent.text_token[index] in world.objects:
                    add_attributes(sent, c, sent.text_token[index], world, "", DBO_Concept.HAS)
                    obj = world.objects[sent.text_token[index]]
                    obj.timesMentioned += 1
                    sent.finished_nodes[index] = 1
                else:
                    add_objects(sent, compound_extraction(sent, str(sent.text_token[index])), sent.dep[index], lemma,
                                world)
                    add_attributes(sent, c, compound_extraction(sent, str(sent.text_token[index])), world, "",
                                   DBO_Concept.HAS)
    if dep in ["attr", "appos"]:
        add_attributes(sent, child, subject, world, "", DBO_Concept.IS_A)
    if dep in ["dobj", "relcl"]:
        if subject:
            add_attributes(sent, child, subject, world, "", DBO_Concept.HAS)


def check_duplicate_attribute(obj_attributes, attribute):
    for i in obj_attributes:
        if i.name == attribute.name:
            if i.isNegated is not attribute.isNegated:
                i.isNegated = attribute.isNegated
            return None
    return attribute


def add_attributes(sent, child, subject, world, negation="", relation=""):
    list_of_attributes = [child.lower()]
    list_of_char = char_conj_extractions(sent, subject)
    head = child.lower()

    if relation == "":
        relation = DBO_Concept.HAS_PROPERTY

    for i in range(0, len(sent.words)):
        if (sent.dep[i] == 'conj') and (sent.head_text[i] == str(head)):
            list_of_attributes.append(sent.text_token[i].lower())
            head = sent.text_token[i].lower()
            sent.finished_nodes[i] = 1

    print("LIST OF ATTR", list_of_attributes)

    for c in list_of_char:
        c = str(c).lower()
        if c in world.characters:
            for attr in list_of_attributes:
                attr = attr.lower()
                new_attribute = Attribute(relation, attr, negation)
                char = world.characters[c]
                print("ADD", attr, "TO", c)

                new_attribute = check_duplicate_attribute(char.attributes, new_attribute)
                if new_attribute is not None:
                    char.attributes.append(new_attribute)

                    if not relation == DBO_Concept.IS_A:
                        print("RELATION", relation)
                        char.type.append(attr)

        elif c in world.objects:
            for attr in list_of_attributes:
                attr = attr.lower()
                new_attribute = Attribute(relation, attr, negation)
                print("ADD", attr, "TO", c)
                obj = world.objects[c]

                new_attribute = check_duplicate_attribute(obj.attributes, new_attribute)
                if new_attribute is not None:
                    print(" ---------------------- ADDED IT ------------------------")
                    obj.attributes.append(new_attribute)

                    if relation == DBO_Concept.IS_A:
                        print("RELATION", relation)
                        obj.type.append(attr)


def add_settings(sent, num, subject, negation, world):

    if sent.location:
        current_location = sent.location
    else:
        current_location = {'LOC': None, 'DATE': None, 'TIME': None}

    list_of_char = []
    is_setting = False
    if subject:
        list_of_char = char_conj_extractions(sent, subject)

    if not negation:
        ent_index = find_ent_index(sent, str(sent.text_token[num]))
        if ent_index is not None:
            label = sent.label[ent_index]
            ent_text = sent.text_ent[ent_index]
        else:
            label = ""
            ent_text = sent.text_token[num]
        ent_text = str(ent_text).lower()

        if ent_text not in world.settings:

            is_location = \
                label in ["LOC", "GPE"] or \
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "place") or \
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "location") or\
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "site")

            is_date_time = \
                label in ["DATE", "TIME"] or \
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "time period")

            if is_location or is_date_time:

                if is_location:
                    type_name = "LOC"
                else:
                    type_name = "TIME"

                is_setting = True
                new_setting = Setting()
                new_setting.id = ent_text
                new_setting.name = ent_text
                new_setting.type = type_name
                current_location[type_name] = ent_text
                world.add_setting(new_setting)

            sent.location = current_location

        else:
            is_setting = True

            if world.settings[str(sent.text_token[num])].type == "LOC":
                current_location["LOC"] = ent_text
            elif world.settings[str(sent.text_token[num])].type == "TIME":
                current_location["TIME"] = ent_text

        for c in list_of_char:
            if str(c) in world.characters and current_location:
                char = world.characters[str(c)]
                for key, value in current_location.items():
                    if value:
                        char.inSetting[key] = value
            elif str(c) in world.objects and current_location:
                obj = world.objects[str(c)]
                for key, value in current_location.items():
                    if value:
                        obj.inSetting[key] = value
    return is_setting


# ---------- rachel

CAT_STORY = 1
CAT_COMMAND = 2
CAT_ANSWER = 3
#ie_categorizing
def getCategory(sentence):
    #checks if entry has "orsen"
    if 'orsen' in sentence or 'orson' in sentence or 'Orson' in sentence or 'Orsen' in sentence:
        return CAT_COMMAND
    elif 'yes' in sentence or 'no' in sentence:
        return CAT_ANSWER
    else:
        return CAT_STORY


def coref_resolution(s, sent_curr, sent_bef, world, isFirst):
    prn =  []
    noun = []
    curr = sent_curr
    bef = sent_bef
    none = {0: None}
    coref = Coref()

    num_prn = 0
    num_conj = 0
    num_pron = 0

    for x in range(0, len(s.pos)):
        if s.tag[x] == 'PRP' or s.tag[x] == 'PRP$':
            num_prn += 1
        if s.pos[x] == 'CCONJ':
            num_conj += 1
        if s.lemma[x] =='-PRON-':
            num_pron += 1

    for x in range(0, num_prn):
        if num_conj >= 1:
            sent = coref.continuous_coref(utterances=sent_curr)
            num_conj -=1
        elif isFirst is False:
            sent = coref.one_shot_coref(utterances=sent_curr, context=sent_bef)

        mentions = coref.get_mentions()
        # print("mentions", mentions)

        rep = coref.get_most_representative()
        print("rep", rep)
        scores = coref.get_scores()
        print("scores", scores)
        propn_count = 0
        noun_count = 0

        for i in range(0, len(s.text_token)):
            #print(s.tag)
            if s.pos[i] == 'PROPN':
                propn_count += 1
            if s.tag[i] == 'NN':
                noun_count += 1

        #print("noun", noun_count)
        if propn_count < 1:
            if noun_count < 1 and isFirst is True:
                return sent_curr

        if len(rep) > 0 and len(scores)>0:
            count = 0

            add_apos = []
            for key, value in rep.items():
                if str(key).lower() == "his" or str(key).lower() == "hers" or str(key).lower() == "their" or str(key).lower() == "our" or str(key).lower() == "its":
                    add_apos.append(count)
                count +=1
            c = 0
            for key, value in rep.items():
               for i in range(0, len(add_apos)):
                   if add_apos[i] == c:
                       sent_curr = sent_curr.replace(str(key), str(value) + "'s")

            c += 1
            hold_key = " " + str(key) + " "
            hold_val = " " + str(value) + " "
            sent_curr = sent_curr.replace(hold_key, hold_val)

            if (str(value) not in world.characters) and (str(value) not in world.objects):
                if (str(key).lower() == "he") or (str(key).lower() == "his") or (str(key).lower() == "him"):
                    new_character = Character()
                    new_character.name = str(value)
                    new_character.id = str(value)
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned += 1
                elif (str(key).lower() == "she") or (str(key).lower() == "her") or (str(key).lower() == "hers"):
                    new_character = Character()
                    new_character.name = str(value)
                    new_character.id = str(value)
                    new_character.gender = "F"
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned += 1

        elif len(scores.get('single_scores')) > 1:
            # extract scores
            single_mention = scores.get('single_scores')
            pair_mention = scores.get('pair_scores')
            single_sc_lib = []
            pair_sc_lib = []
            #
            # print("Single", single_mention)
            # print("Pair", pair_mention)

            count = 0
            for i in range(0, len(single_mention)):
                if single_mention.get(i) == none.get(0):
                  # print("None here")
                  count += 1
                else:
                  single_sc_lib.append(float(single_mention.get(i)))

            #count -=1
            # print("COUNT", count)
            # print("SINGLE_SC_LIB", single_sc_lib)
            #
            # print("INDEX min", single_sc_lib.index(min(single_sc_lib)))
            low_single_index = single_sc_lib.index(min(single_sc_lib))
            low_single_index += count

            #print("found it low_single_index: ", low_single_index)
            holder = {}

            #print(pair_mention.get(low_single_index))
            holder = pair_mention.get(low_single_index)

            #print("holder", len(holder))
            for i in range(0, len(holder)):
                pair_sc_lib.append(holder.get(i))

            #print("PAIR!!!!!!!!!!!", pair_sc_lib)
            high_pair_index = pair_sc_lib.index(max(pair_sc_lib))
            #print("found it high_pair_index: ", high_pair_index)

            prn.append(mentions[low_single_index])
            noun.append(mentions[high_pair_index])
            print(noun, prn)
            #print("numPron", num_pron)


            for i in range(0, len(prn)):
                for k in range(0, len(s.text_token)):
                    #print("ASAIFHA", str(noun[i]), s.text_token[k])
                    if s.text_token[k] in str(noun[i]):
                        if s.pos[k] != 'NOUN' or s.pos[k] != 'PROPN':
                            return sent_curr
                #print("SENTENCE", sent_curr)
                sent_curr = sent_curr.replace(str(prn[i]), str(noun[i]))

        else:
            print("OWN CODE")
            print(s.text_token)
            isThis = ""
            changeThis = ""
            for i in range(0, len(s.text_token)):
                if s.dep[i] == 'nsubj' and (s.pos[i] == 'PROPN' or s.pos[i] == 'NOUN'):
                    #print(s.dep[i], "check prop or noun", s.pos[i])
                    isThis = s.text_token[i]
                    for j in range(0, len(s.text_token)):
                        if s.dep[j] == 'nsubj' and s.pos[j] == 'PRON' or s.tag[j] =='PRP$' or s.tag[j] == 'PRP':
                            #print(s.dep[j], "check pron", s.pos[j])
                            changeThis = s.text_token[j]

                elif s.pos[i] == 'NOUN' or s.pos[i] == 'PROPN':
                    isThis = s.text_token[i]
                    for j in range(0, len(s.text_token)):
                        if s.dep[j] == 'nsubj' and s.pos[j] == 'PRON' or s.tag[j] =='PRP$' or s.tag[j] == 'PRP':
                            #print(s.dep[j], "check pron", s.pos[j])
                            changeThis = s.text_token[j]

                if len(isThis) > 0 and len(changeThis) > 0:
                    if changeThis.lower() == 'her' or changeThis.lower() == 'his' or changeThis.lower() == 'our':
                        isThis = isThis + "'s"

                    split = sent_curr.split(" ")
                    for i in range(0, len(split)):
                        if split[i] == changeThis:
                            split[i] = isThis
                    sent_curr = " ".join(split)

    return sent_curr


    #rep = coref.get_most_representative()
    #print("rep", rep)

def isAction(sentence):
    isAction = False
    be_forms = ["is", "are", "am", "were", "was", "feels", "looks"]
    for k in range(0, len(be_forms)):
        for i in range(0, len(sentence.text_token)):
            if be_forms[k] == sentence.text_token[i]:
                isAction = True

    return isAction

def checkProceed(dep_root, xcomp_count, acomp_count, dobj_count, attr_count, pobj_count):
    total = 0

    if (dep_root == 'xcomp'):
        xcomp_count -= 1
    if (dep_root == 'acomp'):
        acomp_count -= 1
    if (dep_root == 'dobj'):
        dobj_count -= 1
    if (dep_root == 'attr'):
        attr_count -= 1
    if (dep_root== 'pobj'):
        pobj_count -=1

    total = xcomp_count + acomp_count + dobj_count  + attr_count + pobj_count

    if total > 0:
        return True
    else:
        return False

#ie_event_extract
def event_extraction(sentence, world, current_node):
    print("-------------- Entering EVENT EXTRACTION -----------------")
    event_char = []
    event_char_action = []
    event_obj = []
    event_obj_action = []
    event_type = []
    event_loc = []

    #get list of characters and objects from world
    nsubj_count = 0
    verb_count = 0

    cc_count = 0
    conj_count = 0

    dobj_count = 0
    acomp_count = 0
    xcomp_count = 0
    attr_count = 0
    pobj_count = 0
    advmod_count = 0

    #getting the subject count
    for i in range(0, len(sentence.dep_root)):
        if sentence.dep_root[i] == 'nsubj' or sentence.dep_root[i] == 'nsubjpass':
            nsubj_count += 1
        elif sentence.dep_root[i] == 'conj':
            conj_count += 1

    for i in range(0, len(sentence.pos)):
        if sentence.pos[i] == 'VERB':
            verb_count += 1
    for i in range(0, len(sentence.dep)):
        if sentence.dep[i] == 'acomp':
            acomp_count += 1
        elif sentence.dep[i] == 'xcomp':
            xcomp_count += 1
        elif sentence.dep[i] == 'attr':
            attr_count += 1
        elif sentence.dep[i] =='conj':
            cc_count += 1
        elif sentence.dep[i] == 'pobj':
            pobj_count += 1
        elif sentence.dep[i] == 'dobj':
            dobj_count += 1
        elif sentence.dep[i] == 'advmod':
            advmod_count += 1

    #print("nsubj", nsubj_count)
    #print("dobj", dobj_count)
    #print("acomp", acomp_count)
    #print("xcomp", xcomp_count)
    #print("conj", conj_count)

    #print("TOKEN", sentence.text_token)
    for x in range(0, len(sentence.text_token)):
        isFound_char = False
        isFound_char_action = False
        isFound_obj = False
        isFound_obj_action = False

        #print("NSUBJ COUNT", nsubj_count)
        if nsubj_count > 0:
            #Start of Getting Character and Character Action
            if sentence.dep[x] == 'nsubj' or sentence.dep[x] == 'nsubjpass':
                isComp_char = False
                isComp_char_action = False
                isNeg_char_action = False
                isFound_char_action = False
                isDesc = False
                nsubj_count -= 1

                c = sentence.text_token[x]
                c = compound_extraction(sentence, sentence.text_token[x])
                hold_char = [c]
                head_char = c
                #print("head_char", c)
                #head_char = compound_extraction(sentence, head_char)

                #print("TOKEN", sentence.text_token)
                for i in range(0, len(sentence.text_token)):
                    #print(sentence.head_text[i], "checking", head_char)
                    # print("headtext", sentence.head_text[i], head_char)
                    if (sentence.dep[i] == 'conj') and sentence.head_text[i].lower() == head_char:
                        #h = compound_extraction(sentence, sentence.text_token[i])
                        # print("it the same")
                        hold_char.append(sentence.text_token[i])
                        isComp_char = True
                        head_char = sentence.text_token[i]
                        #print("HEADTEXT", sentence.head_text[i])
                        #print("HEAD", head_char)


                    if sentence.head_text[i] != head_char and (sentence.pos[i] == 'VERB'):
                         hold_char_action = [sentence.head_text[x]]
                         head_char_action = sentence.head_text[x]

                         if sentence.pos[i-1] == 'VERB' and sentence.dep[i-1] == 'aux':
                             head_char_action = sentence.text_token[i-1] + " " + sentence.head_text[x]
                             hold_char_action = [head_char_action]
                         #subj_checker = sentence.text_token[x]
                         # print("HERE IS A VERB")
                         # print("TOKEN", sentence.text_token)

                         if sentence.dep[i-1] == 'neg' and sentence.head_text[i-1] == sentence.head_text[x]:
                             head_char_action = sentence.text_token[i-1] + " " + sentence.head_text[x]
                             hold_char_action = [head_char_action]
                             isNeg_char_action = True

                         if (i+1) < len(sentence.dep):
                             if sentence.dep[i+1] == 'neg' and sentence.head_text[i+1] == sentence.head_text[x]:
                                 head_char_action = sentence.head_text[x] + " " + sentence.text_token[i+1]
                                 hold_char_action = [head_char_action]
                                 isNeg_char_action = True

                         if (i+1) < len(sentence.text_token):
                            if sentence.dep[i + 1] == 'prep':
                                head_char_action = sentence.text_token[i] + " " + sentence.text_token[i + 1]
                                hold_char_action = [head_char_action]
                                if sentence.text_token[i+1] == 'like':
                                    isDesc = True

                         isNeg = False
                         for i in range(0, len(sentence.text_token)):
                            if (sentence.dep[i] == 'conj') and \
                                    (sentence.head_text[i] in head_char_action) and verb_count > 0:
                                verb_count -= 1

                                if sentence.dep[i - 1] == 'neg' and sentence.head_text[i - 1] == sentence.text_token[i]:
                                    h = sentence.text_token[i - 1] + " " + sentence.text_token[i]
                                    isNeg = True

                                if isNeg is True:
                                    hold_char_action.append(h)
                                else:
                                    hold_char_action.append(sentence.text_token[i])

                                isComp_char_action = True
                                head_char_action = sentence.text_token[i]

                                #print("HEADTEXT", sentence.head_text[i])
                                #print("HEAD", head_char_action)

                    #print("HOLDCHARACTION", hold_char_action)

                if isComp_char_action is True:
                    event_char_action.append(",".join(hold_char_action))

                    pos = len(event_char_action)-1
                    if isNeg_char_action is True and 'not' not in event_char_action[pos]:
                        event_char_action[pos] = "not " + event_char_action[pos]

                    isFound_char_action = True
                else:
                    event_char_action.append(hold_char_action[0])
                    isFound_char_action = True

                if isFound_char_action is True:
                    if isAction(sentence) is False:
                        # print("HELLO I'M AN ACTION")
                        event_type.append(FRAME_EVENT)
                    else:
                        event_type.append(FRAME_DESCRIPTIVE)
                #print("HOLDCHAR", hold_char)
                #print("ISCOMP", isComp_char)

                if isComp_char is True:
                    event_char.append(",".join(hold_char))
                else:
                    event_char.append(hold_char[0])
                    print("event_char", event_char)
            #End of Getting Character

        #print("TEXT TOKEN", sentence.text_token)
        #print("ROOT", sentence.dep_root)
        #Start of Getting Object and Object Action
        total_obj = xcomp_count + acomp_count + dobj_count + attr_count + pobj_count + advmod_count
        #print("total", total_obj)
        if total_obj > 0:
            isComp_obj = False
            isComp_obj_action = False
            isFound_obj_action = False
            isAdded_obj = False
            for i in range(0, len(sentence.dep)):
                #isProceed = checkProceed(sentence.dep[x], xcomp_count, acomp_count, dobj_count, attr_count, pobj_count)
                #if (sentence.dep[x] == 'xcomp') or (sentence.dep[x] == 'acomp') or (sentence.dep[x] == 'dobj') or \
                #        (sentence.dep[x] == 'attr') or (sentence.dep[x] == 'pobj'):
                #print(sentence.dep[i])
                #print(sentence.dep)
                #hold_obj = []
                if sentence.dep[i] == 'xcomp':
                    xcomp_count -= 1
                    o = sentence.text_token[i]
                    o = compound_extraction(sentence, sentence.text_token[i])
                    hold_obj = [o]
                    head_obj = o

                    if sentence.dep[i-1] == 'aux':
                        head_obj = sentence.text_token[i-1] + " " + sentence.text_token[i]
                        hold_obj = [head_obj]

                    isFound_obj = True
                    #print(head_obj)
                elif sentence.dep[i] == 'acomp':
                    acomp_count -= 1
                    o = sentence.text_token[i]
                    o = compound_extraction(sentence, sentence.text_token[i])
                    # print("O", o)
                    hold_obj = [o]
                    head_obj = o

                    isFound_obj = True

                elif sentence.dep[i] == 'dobj':
                    dobj_count -= 1
                    o = sentence.text_token[i]
                    o = compound_extraction(sentence, sentence.text_token[i])
                    # print("O", o)
                    hold_obj = [o]
                    head_obj = o

                    isFound_obj = True
                elif sentence.dep[i] == 'attr':
                    attr_count -= 1
                    #print(sentence.text_token[i])
                    #print("Attribute found")
                    o = sentence.text_token[i]
                    o = compound_extraction(sentence, sentence.text_token[i])
                    # print("O", o)
                    hold_obj = [o]
                    head_obj = o

                    isFound_obj = True
                elif sentence.dep[i] == 'pobj':
                    pobj_count -= 1
                    o = sentence.text_token[i]
                    o = compound_extraction(sentence, sentence.text_token[i])
                    hold_obj = [o]
                    head_obj = o

                    isFound_obj = True
                elif sentence.dep[i] == 'advmod':
                    advmod_count -= 1
                    o = sentence.text_token[i]
                    o = compound_extraction(sentence, sentence.text_token[i])
                    hold_obj = [o]
                    head_obj = o

                    isFound_obj = True
                if isFound_obj is True:
                    #head_obj = compound_extraction(sentence, head_obj)
                    #print("it is True")
                    #print("TOKEN", sentence.text_token)
                    isNeg = False
                    for i in range(0, len(sentence.text_token)):
                        if (sentence.dep[i] == 'conj') and sentence.head_text[i] == head_obj:
                            # print(sentence.head_text[i-1], "vs", sentence.head_text[i])
                            if sentence.dep[i - 1] == 'neg' and sentence.head_text[i - 1] == sentence.text_token[i]:
                                h = sentence.text_token[i - 1] + " " + sentence.text_token[i]
                                isNeg = True

                            if isNeg is True:
                                hold_obj.append(h)
                            else:
                                hold_obj.append(sentence.text_token[i])

                            isComp_obj = True
                            head_obj = sentence.text_token[i]
                            #print("HEADTEXT", sentence.head_text[i])
                            #print("HEAD", head_obj)


                        if sentence.head_text[i] != head_obj:
                            hold_obj_action = [sentence.head_text[x]]
                            head_obj_action = sentence.head_text[x]

                            for x in range(0, len(sentence.text_token)):
                                # print("HERE IS A VERB")
                                # print("TOKEN", sentence.text_token)

                                for i in range(0, len(sentence.text_token)):
                                    if (sentence.dep[i] == 'conj') and (sentence.head_text[i] == head_obj_action):
                                        hold_obj_action.append(sentence.text_token[i])
                                        isComp_obj_action = True
                                        head_obj_action = sentence.text_token[i]


                    #if isComp_obj_action is True:
                    #    event_obj_action.append(",".join(hold_obj_action))
                    #    isFound_obj_action = True
                    #else:
                    #    event_obj_action.append(hold_obj_action[0])
                    #    isFound_obj_action = True

                    if isComp_obj is True and isAdded_obj is False:
                        #print("HOLDOBJ", hold_obj)
                        event_obj.append(",".join(hold_obj))
                        isAdded_obj = True
                    elif isAdded_obj is False:
                        #print("HOLDOBJ", hold_obj)
                        #print("ADDED THE THING")
                        event_obj.append(hold_obj[0])
                        isAdded_obj = True

        #End of Getting Object and Object Action

        #GET OBJECT AND CHECK IF ACTION SENTENCE
        #if xcomp_count > 0:
        #    if sentence.dep[x] == 'xcomp':
        #        event_obj.append(sentence.lemma[x])
        #print("cc", cc_count)

        #if dobj_count > 0 and isAction(sentence) is False:
            #print("IM AN ACTION")
        #    if sentence.dep_root[x] == 'dobj':
        #        dobj_count -= 1
                #print("dobj", sentence.dep_root_head[x])
        #        obj = sentence.text_chunk[x]
                #print("obj", sentence.text_chunk[x])
        #        if cc_count > 0 and isFound_obj is False:
        #            for i in range(0, len(sentence.text_token)):
        #                if sentence.dep[i] == 'conj' and sentence.head_text[i] == obj:
                            #print("STILL ENTERING")
        #                    event_obj.append(obj + " and " + sentence.text_token[i])
        #                    isFound_obj = True
        #        elif conj_count == 0 and isFound_obj is False:
                    #print("STILL ENTERING")
        #            event_obj.append(obj)
        #            isFound_obj = True

          #     match the object with the list of objects from the world
          #     for y in range(0, len(list_obj)):
          #        if char == list_obj.name[y] and isFound_obj is False:
          #           event_obj.append(obj)
          #          isFound_obj = True

          #     add object action action
          #     event_obj_action.append(sentence.dep_root_head[x])

        #GET OBJECT AND CHECK IF DESCRIPTIVE SENTENCE
        #if (acomp_count > 0 or attr_count > 0) and isAction(sentence) == True:
        #    if sentence.dep[x] == 'acomp' or sentence.dep[x] == 'attr':
        #        obj = sentence.lemma[x]
        #        #print("cc_count", cc_count)
        #        if cc_count > 0 and isFound_obj is False:
        #            for i in range(0, len(sentence.text_token)):
        #                #print("DEP", sentence.dep[i], "HEADTEXT", sentence.head_text[i])
        #                if sentence.dep[i] == 'conj' and sentence.head_text[i] == obj:
        #                   event_obj.append(obj + " and " + sentence.text_token[i])
        #                    isFound_obj = True
        #        elif isFound_obj is False:
        #            #print("STILL ENTERING")
        #            event_obj.append(obj)
        #            isFound_obj = True


    #if len(event_obj) > 0:
    #    event_obj_com = []
    #    event_obj = ",".join(event_obj)
    #    event_obj_com.append(event_obj)

    #    add_event(event_type, event_char, event_char_action, event_obj_com, event_obj_action, event_loc, world)

    #    print("---- EVENT FRAME ----")
    #    print("Type", event_type, "Char", event_char, "Char_Action", event_char_action, "Obj", event_obj_com, "Obj_Action", event_obj_action, "LOC", event_loc)
    #else:
        #print("LEN OBJ", len(event_obj))
        #print("LEN CHAR", len(event_char))

    add_event(event_type, event_char, event_char_action, event_obj, event_obj_action, event_loc, world)

    #print("---- EVENT FRAME ----")
    #print("Type", event_type, "Char", event_char, "Char_Action", event_char_action, "Obj", event_obj, "Obj_Action", event_obj_action, "LOC", event_loc)

#Add event to the world
def add_event(type, char, char_action, obj, obj_action, loc, world):

    #print("LEN OBJ", len(obj))
    for x in range(0, len(char)):
        addObj = ""
        addChar = ""
        new_eventframe = EventFrame()

        if len(type) > 0:
            new_eventframe.type = type[x]
        if len(loc) > 0:
            new_eventframe.setting = loc[x]
        if len(char) > 0:
            #list_char = world.characters
            #list_obj = world.objects
            #isObj = False

            #print("hello")
            #for k in list_obj:
                #print("NOT A CHARACTER")
            #    for j in list_obj:
            #        if list_obj[j].name == char[x]:
            #            #print(list_obj[j].name)
            #            addObj = char[x]
            #            char[x] = ""
            #            isObj = True

            #if isObj is False:
            new_eventframe.doer = char[x]

        if len(char_action) > 0:
            new_eventframe.doer_actions = char[x] + ":" + char_action[x]

        if x < len(obj):
            #list_char = world.characters
            #ist_obj = world.objects
            #for k in list_char:
            #    if list_char[k].name == obj[x]:
            #        addChar = obj[x]
            #        obj[x] = ""

            #if addObj != "":
            #    obj[x] == addObj + "," + obj[x]
            #    new_eventframe.receiver = obj[x]
            #else:
            new_eventframe.receiver = obj[x]

            if addChar != "":
                new_eventframe.doer = new_eventframe.doer + "," + addChar
                new_eventframe.doer_actions = new_eventframe.doer + ":" + new_eventframe.doer_actions
            #new_eventframe.receiver = obj[x]
        if x < len(obj_action):
            new_eventframe.receiver_actions = obj[x] + ":" + obj_action[x]

        for i in range(0, len(char)):
            loc_char = world.characters
            for k in loc_char:
                if loc_char[k].name in char[i]:
                    print(loc_char[k])
                    new_eventframe.setting = loc_char[k].inSetting

        world.add_eventframe(new_eventframe)
        print("---- EVENT ADDED TO THE WORLD ----")

    print(world.event_chain)
    for item in world.event_chain:
        print(item)

        #    event_char.append(char + " and " + sentence.text_token[i])
        #    print("headtext", sentence.head_text[x])

        #    if sentence.head_text[x] != char:
        #        char_action = sentence.head_text[x]
        #        print("conj", conj_count, isFound_char_action )
        #        if cc_count > 0 and isFound_char_action is False:
        #            for i in range(0, len(sentence.text_token)):
        #                print("ENTER COMBO CHAR ACT")
        #                print("dep", sentence.dep[i], "head", sentence.head_text[i])

        #               if sentence.dep[i] == 'conj' and sentence.head_text[i] == char_action:
        #                    print("is this true")
        #                    event_char_action.append(char_action + " and " + sentence.text_token[i])
        #                    isFound_char_action = True

        #        if isFound_char_action is False:
        #            event_char_action.append(char_action)
        #            isFound_char_action = True

        #    isFound_char = True

#    if isFound_char  is False:
#        event_char.append(char)
#        print("headtext", sentence.head_text[x])
#        char_action = sentence.head_text[x]
#        if cc_count > 0 and isFound_char_action is False:
#            for i in range(0, len(sentence.text_token)):
#                if sentence.dep[i] == 'conj' and sentence.head_text[i] == char_action:
#                    # print("is this true")
#                    event_char_action.append(char_action + " and " + sentence.text_token[i])
#                    isFound_char_action = True

#        if isFound_char_action is False:
#            event_char_action.append(char_action)
#            isFound_char_action = True

#        if isAction(sentence) is False:
#            print("HELLO I'M AN ACTION")
#            event_type.append(FRAME_EVENT)
#        else:
#            event_type.append(FRAME_DESCRIPTIVE)

#        isFound_char = True
