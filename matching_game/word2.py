#word2.py

class Word():
	def __init__(self, _word, _phoneme, _grapheme, _sounds):
		self.word = _word
		self.phoneme = _phoneme
		self.spelling_pattern = _grapheme
		self.sounds = _sounds

	def __str__(self):
		return "%s" %self.word

	def __eq__(self, other_word_str):
		return self.word == other_word_str

	def has_same_phoneme_as(self, other_word):
		return (self.phoneme == other_word.phoneme)

	def has_same_spelling_pattern_as(self, other_word):
		return (self.spelling_pattern == other_word.spelling_pattern)

	def has_same_spelling_pattern_and_phoneme_as(self, other_word):
		return (self.spelling_pattern == other_word.spelling_pattern and self.phoneme == other_word.phoneme)
