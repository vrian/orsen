class Object:

    id = ""
    name = ""
    type = []
    inSetting = {}
    timesMentioned = 0
    attributes = []

    def __init__(self, id="", name="", type=[], inSetting=0, times=1, attr=[]):
        self.id   = id
        self.name       = name
        self.type       = type
        self.inSetting  = inSetting
        self.timesMentioned = times
        self.attributes = attr

    def __str__(self):
        return "OBJECT %s: \nName: %s \nType: %s \ninSetting: %s \nmentioned: %s\n" \
               % (str(self.id), self.name, self.type, self.inSetting, str(self.timesMentioned))\
               + " attributes: %s" + str(self.attributes)
