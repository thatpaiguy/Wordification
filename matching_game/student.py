class Student():
	def __init__(self, _username, _level):
		self.username = _username
		self.level = _level
		self.counter = 0
		for i in range(9):
			self.counter+=1

	def get_counter(self):
		return self.counter
	def __str__(self):
		return "%s - Level %i speller" %(self.username, int(self.level))
