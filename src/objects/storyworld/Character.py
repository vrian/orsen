from .Object import Object
from .Setting import Setting

class Character(Object):

    gender = ""
    desire = ""
    feeling = ""

    def __init__(self, idChar="", name="", typeChar="", inSetting=0, times=0, attr=[], gender="", desire="", feeling=""):
        super().__init__(idChar, name, typeChar, inSetting, times, attr)
        self.gender = gender
        self.desire = desire
        self.feeling = feeling

    def __str__(self):
        return "CHARACTER: %s \nName: %s \nGender: %s \ndesire: %s \nType: %s \ninSetting: %s \nmentioned: %d \nfeeling: %s\n" \
               % (self.id, self.name, self.gender, self.desire, self.type, self.inSetting, self.timesMentioned, self.feeling)\
               + "attributes: " + str(self.attributes)
    
    @staticmethod
    def convert_from_object(object):
        new_char = Character(object.id, object.name, object.type, object.inSetting, object.timesMentioned, object.attributes)
        return new_char

    @staticmethod
    def convert_from_setting(setting):
        new_char = Character(setting.id, setting.id)

        if setting.time != "" :
            new_char.inSetting = Setting(setting.time,setting.time, time=setting.time)

        return new_char