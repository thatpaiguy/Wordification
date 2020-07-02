class MatchingWord():
    def __init__(self, in_string):
        init_arr = in_string.split("$")
        self.name = init_arr[0]
        self.phoneme_seq = init_arr[1]
        self.is_main = bool(int(init_arr[2]))

    def __eq__(self, target):
        return self.phoneme_seq == target.phoneme_seq
    def __str__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)
