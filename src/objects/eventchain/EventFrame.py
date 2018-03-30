from ..storyworld.Object    import Object
from ..storyworld.Setting   import Setting

FRAME_EVENT = 0
FRAME_DESCRIPTIVE = 1

class EventFrame:

    event_type = -1
    # descriptive, action, etc.

    def __init__(self, seq_no=-1, type="", doer=None, doer_actions=[], receiver=None, receiver_actions=[], setting=None, event_type=-1):
        self.sequence_no        = seq_no
        self.type               = type
        self.doer               = doer
        self.doer_actions       = doer_actions
        self.receiver           = receiver
        self.receiver_actions   = receiver_actions
        self.setting            = setting
        self.event_type         = event_type

    def __str__(self):
        return str(self.sequence_no) + "-" + str(self.event_type) +\
               "\n"+"DOER:"+ str(self.doer) +"\n"+"D-ACTIONS:"+str(self.doer_actions)+\
               "\n"+"REC:"+ str(self.receiver) +"\n"+"R-ACTIONS:"+str(self.receiver_actions)+\
               "\n"+"SETTING:"+str(self.setting)

    def to_sentence_string(self):
        string = "<event sentence>"
        return string

# class EventFrame:
#
#     characters = {}
#     character_actions = {}
#     # character = a Character() object
#     # character_actions is a dict of character names as key connected to an action verb
#     #       ie. { "KAT" : "run" , "John" : "run" }
#
#     objects = {}
#     object_actions = {}
#     # same except for objects
#
#     setting = None
