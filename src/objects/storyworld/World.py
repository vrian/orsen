from operator import attrgetter
class World:

    # WORLD ELEMENTS

    id = -1
    characters = {}
    objects = {}
    relationships = {}
    settings = {}
    event_chain = []

    # RESPONSE ELEMENTS

    # stored as moves
    reponses = []

    empty_response = 0

    def __init__(self, id="-1"):
        self.id = id

    def add_character(self, char):
        if char.id not in self.objects and char.id not in self.characters:
            self.characters[char.id] = char
            return True
        elif char.id in self.objects and char.id not in self.characters:
            self.objects.pop(char.id)
            self.characters[char.id] = char
            return True
        else:
            return False

    def add_object(self, obj):
        if obj.id not in self.objects:
            self.objects[obj.id] = obj
            return True
        else:
            return False

    def add_relationship(self, relationship):
        if relationship.id not in self.relationships:
            self.relationships[relationship.id] = relationship
            return True
        else:
            return False

    def add_setting(self, setting):
        if setting.id not in self.settings:
            self.settings[setting.id] = setting
            return True
        else:
            return False

    def add_eventframe(self, event):
        print("EHST THR FUCK")
        event.seq_no = len(self.event_chain)
        self.event_chain.append(event)

    def get_main_character(self, rank=0):
        sorted_list = sorted(self.characters.values(), key=attrgetter('timesMentioned'), reverse=True)
        final = [sorted_list[rank]]

        for item in sorted_list:
            if item.timesMentioned == sorted_list[rank].timesMentioned:
                final.append(item)

        return final

    def get_top_characters(self, num_of_charas=3):
        sorted_list= sorted(self.characters.values(), key=attrgetter('timesMentioned'), reverse=True)

        if len(sorted_list) > num_of_charas:
            num_of_charas = len(sorted_list)

        return sorted_list[:num_of_charas]

    def get_main_objects(self, rank=0):
        sorted_list = sorted(self.objects.values(), key=attrgetter('timesMentioned'), reverse=True)
        final = [sorted_list[rank]]

        for item in sorted_list:
            if item.timesMentioned == sorted_list[rank].timesMentioned:
                final.append(item)

        return final

    def get_top_objects(self, num_of_charas=3):
        sorted_list = sorted(self.objects.values(), key=attrgetter('timesMentioned'), reverse=True)
        return sorted_list[:num_of_charas]
