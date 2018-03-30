class Sentence:
    words = ""
    text_token = []
    head_text = []
    lemma = []
    pos = []
    tag = []
    dep = []
    children = []

    text_ent = []
    label = []

    text_chunk = []
    dep_root = []
    dep_root_head = []

    finished_nodes = []


    def __init__(self):
        self.words = ""
        self.text_token = []
        self.head_text = []
        self.lemma = []
        self.pos = []
        self.tag = []
        self.dep = []
        self.children = []

        self.text_ent = []
        self.label = []

        self.text_chunk = []
        self.dep_root = []
        self.dep_root_head = []

        self.finished_nodes = []
