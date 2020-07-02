from matching_words import *
from collections import defaultdict
from tkinter import *
from tkinter import font
from random import random as RNG
import time
from pygame import mixer
import threading
import queue
"""
switch test and teach cases

change color of inactive
change buttons to labels in sideboard
display matched cards in columns under corresponding

flip second card,
set color to green if matched
if not matched set color to red
when any other button is clicked these

right and wrong soundfiles

tiles play sounds when clicked
teach:
When two cards have been flipped_up, Say both, then "those words rhyme with <category_word>" or "those words don't rhyme"
Followed by sound

For testing, each color corresponds with one of the target words
Clicking a tile turns that word card that color
Testing word lights up with a specific color
Find 5 words, the accuracy of these words are scored
When the excercise moves on to the next word to test, all the colors are reset

button to play word again

Word sorting:
Recording onsets -> no vowel or vowel?

Filtering options

"""
background = "#294777"
flipped_up = "#55a0d6"
flipped_down = "#ed9f47"
inactive = "#294777"#"#f9be7a"
incorrect = "#ef5656"
correct = "#38ea85"
color_list = ["#f48042", "#caf441", "#41f4ac", "#41d0f4", "#4170f4", "#7f41f4", "#f44182", "#a81900"]
lock = threading.Lock()
q = queue.Queue()
max_queue_size = 10
def worker():
    print("Worker spawned")
    while True:
        if not q.empty():
            soundfile = q.get()
            if soundfile is not None:
                mixer.music.load(soundfile)
                mixer.music.play()
                while mixer.music.get_busy()>0:
                    pass
            elif soundfile is None:
                break
            q.task_done()

class Game():
    def __init__(self):
        #map words to the table by phones
        self.word_map = defaultdict(list)
        self.word_list = []
        self.word_categories = []
        self.active_elements = []
        self.selected_elements = []
        self.sideboard_elements = []
        self.active_sideboard_elements = []
        mixer.init()
        self.goal_word = ""
        self.global_hidden = '{:^20}'.format("\n~\n")
        with open('../datafiles/matching_data.csv') as infile:
            for line in infile:
                new_word = MatchingWord(line)
                print(line)
                if new_word.is_main:
                    #print("pushing to ca")
                    self.word_categories.append(new_word)
                else:
                    self.word_map[new_word.phoneme_seq].append(new_word)
        self.build_root()
        t = threading.Thread(target=worker)
        t.start()
        self.root.mainloop()
        q.put(None)

    def build_root(self):
        print("Rendering Root")
        self.root = Tk()
        self.root.title('Wordification')
        self.root.configure(background=background)
        self.game_canvas = Canvas(self.root, bg =background)
        self.sideboard = Canvas(self.root, bg =background)
        self.app_font = font.Font(family = "Consolas",size=14, weight='bold')
        self.build_excercise_options()
        self.game_canvas.pack()
        self.sideboard.pack()

    def build_excercise_options(self):
        for i in range(3, 9):
            self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = "%i Word Categories (teach)" %i, font = self.app_font,\
                command=lambda data = i: self.create_board_teach(data)))
            self.active_elements[-1].grid(row = i, column = 0)
            if i < 8:
                """
                self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = "%i Word Categories (test)" %i, font = self.app_font,\
                    command=lambda data = i: self.create_board_test(data)))
                self.active_elements[-1].grid(row = i, column = 1)
                """
                self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = "%i Word Categories New (test)" %i, font = self.app_font,\
                    command=lambda data = i: self.create_board_test_new(data)))
                self.active_elements[-1].grid(row = i, column = 1)
        """
        self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = "%i Word Categories New (test)" %i, font = self.app_font,\
            command=lambda data = 3: self.create_board_test_new(data)))

        self.active_elements[-1].grid(row = 9, column = 2)
        """

    def create_board_test(self, category_number):
        self.reset_grid()
        self.complete = 0

        index = 0
        length = 6
        width = category_number+1
        self.word_cat_list = []
        self.word_list_active = []
        self.active_incorrect = []
        self.word_set = set()
        self.goal_word_var = StringVar()

        #change wordcatlist to a set!
        while len(self.word_set) != category_number+1:
            rand_index = int(RNG()*len(self.word_categories))
            self.word_set.add(rand_index)

        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()
        for index in self.word_set:
            self.word_cat_list.append(self.word_categories[index])
            self.sideboard_map[self.word_categories[index]] = 2
            for key in self.word_map[self.word_categories[index].phoneme_seq]:
                self.word_list_active.append(key)

        self.word_list_active = self.shuffle(self.word_list_active)
        rand = int(RNG()*len(self.word_cat_list))
        self.goal_word = self.word_cat_list[rand]
        self.goal_word_var.set("Find words that match with %s" %self.goal_word.name)
        self.sideboard_elements.append(Label(self.sideboard, bg = flipped_down, textvariable = self.goal_word_var, font = self.app_font))
        self.sideboard_elements[-1].grid(row = 0, column = 0, columnspan = width)
        button_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 8, column = 0, columnspan = 6)
        for i in range(len(self.word_cat_list)):
            self.sideboard_columns[self.word_cat_list[i]] = i
            button_text = '{:^10}'.format("%s" %self.word_cat_list[i].name)
            self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
            self.sideboard_elements[-1].grid(row = 1, column = i)
        index = 0
        for i in range(length):
            for j in range(width):
                button_text = '{:^25}'.format("\n%s\n" %self.word_list_active[index].name)
                self.active_elements.append(Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                    command=lambda data = [i, j, self.word_list_active[index], index] : self.flip_test(data)))
                self.active_elements[-1].grid(row = i, column = j)
                index += 1
        audio_string = "../assets/audio/findwords.mp3,../assets/audio/%s.mp3" %self.goal_word
        self.enqueue_soundfiles(audio_string)

    def flip_test(self, data):
        row = data[0]
        column = data[1]
        word = data[2]
        index = data[3]
        audio_string = "../assets/audio/matching/%s.mp3" %word
        self.enqueue_soundfiles(audio_string)

        if word == self.goal_word:

            self.active_elements[index].grid_forget()
            self.active_elements[index] = Label(self.game_canvas, bg = inactive, text = self.global_hidden, font = self.app_font)
            self.active_elements[index].grid(row = row, column = column)
            self.complete += 1

            button_text = '{:^10}'.format("%s" %word)
            self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
            self.sideboard_elements[-1].grid(row = self.sideboard_map[self.goal_word], column = self.sideboard_columns[self.goal_word])
            self.sideboard_map[self.goal_word]+=1
            audio_string = "../assets/audio/correct_tone1.mp3"
            self.enqueue_soundfiles(audio_string)

            if self.complete%6 == 0 and self.complete != len(self.word_list_active)-6:
                index_of_word = self.word_cat_list.index(self.goal_word)
                del(self.word_cat_list[index_of_word])
                rand = int(RNG()*len(self.word_cat_list))
                self.goal_word = self.word_cat_list[rand]
                self.goal_word_var.set("Find words that rhyme with %s" %self.goal_word.name)
                audio_string = "../assets/audio/findwords.mp3,../assets/audio/%s.mp3" %self.goal_word
                thread = threading.Thread(target = self.enqueue_soundfiles, \
                                            args = (audio_string,))
                thread.start()
                for incorrect_tuple in self.active_incorrect:
                    inc_index = incorrect_tuple[0]
                    t_row = incorrect_tuple[1]
                    t_column = incorrect_tuple[2]
                    button_text = '{:^25}'.format("\n%s\n" %self.word_list_active[inc_index].name)

                    self.active_elements[inc_index].grid_forget()
                    self.active_elements[inc_index] = Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                        command=lambda data = [t_row, t_column, self.word_list_active[inc_index], inc_index] : self.flip_test(data))
                    self.active_elements[inc_index].grid(row = t_row, column = t_column)
                self.active_incorrect = []
            if self.complete == (len(self.word_list_active)-6):
                audio_string = "../assets/audio/allcorrect.mp3"
                thread = threading.Thread(target = self.enqueue_soundfiles, \
                                            args = (audio_string,))
                thread.start()

    def create_board_test_new(self, category_number):
        self.reset_grid()
        self.complete = 0
        self.category_index = 0
        index = 0
        length = 6
        width = category_number+1
        self.word_cat_list = []
        self.word_list_active = []
        self.active_incorrect = []
        self.selected_elements = []
        self.selected_element_indices = []
        self.word_set = set()
        self.goal_word_var = StringVar()
        self.notification_string = StringVar()
        self.answers = defaultdict(list)
        while len(self.word_set) != category_number+1:
            rand_index = int(RNG()*len(self.word_categories))
            self.word_set.add(rand_index)

        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()
        for index in self.word_set:
            self.word_cat_list.append(self.word_categories[index])
            self.sideboard_map[self.word_categories[index]] = 2
            for key in self.word_map[self.word_categories[index].phoneme_seq]:
                self.word_list_active.append(key)

        self.word_list_active = self.shuffle(self.word_list_active)
        self.goal_word = self.word_cat_list[self.category_index]

        self.goal_word_var.set("Find 5 words that match with %s" %self.goal_word.name)
        self.sideboard_elements.append(Label(self.sideboard, bg = incorrect, textvariable = self.notification_string, font = self.app_font))
        self.sideboard_elements[-1].grid(row = 9, column = 0, columnspan = 3*width//4)

        self.sideboard_elements.append(Label(self.sideboard, bg = flipped_down, textvariable = self.goal_word_var, font = self.app_font))
        self.sideboard_elements[-1].grid(row = 0, column = 0, columnspan = 3*width//4)

        button_text = '{:^5}'.format("Play Again")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda data = "../assets/audio/%s.mp3" %self.goal_word: self.enqueue_soundfiles(data)))
        self.sideboard_elements[-1].grid(row = 0, column = 3*width//4, columnspan = 1*width//4)

        button_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 8, column = 0, columnspan = width//2)

        button_text = '{:^10}'.format("\nConfirm Selection\n")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda : self.submit()))
        self.sideboard_elements[-1].grid(row = 8, column = width//2, columnspan = width//2)

        for i in range(len(self.word_cat_list)):
            self.sideboard_columns[self.word_cat_list[i]] = i
            button_text = '{:^10}'.format("%s" %self.word_cat_list[i].name)
            self.sideboard_elements.append(Label(self.sideboard, bg = color_list[i], text = button_text, font = self.app_font))
            self.sideboard_elements[-1].grid(row = 1, column = i)
        index = 0
        for i in range(length):
            for j in range(width):
                button_text = '{:^25}'.format("\n%s\n" %self.word_list_active[index].name)
                self.active_elements.append(Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                    command=lambda data = [i, j, self.word_list_active[index], index, False] : self.flip_test_new(data)))
                self.active_elements[-1].grid(row = i, column = j)
                index += 1

        audio_string = "../assets/audio/findwords.mp3,../assets/audio/%s.mp3" %self.goal_word
        thread = threading.Thread(target = self.enqueue_soundfiles, \
                                    args = (audio_string,))
        thread.start()

    def flip_test_new(self, data):
        row = data[0]
        column = data[1]
        word = data[2]
        index = data[3]

        selected = data[4]
        button_text = '{:^25}'.format("\n%s\n" %word.name)
        if not selected:
            audio_string = "../assets/audio/matching/%s.mp3" %word
            thread = threading.Thread(target = self.enqueue_soundfiles, \
                                        args = (audio_string,))
            thread.start()
            self.selected_elements.append((word, index, row, column))

            print(len(self.selected_elements))
            self.active_elements[index].grid_forget()
            self.active_elements[index] = Button(self.game_canvas, bg = color_list[self.category_index], \
                                            text = button_text, font = self.app_font,\
                                            command=lambda data = [row, column, \
                                            self.word_list_active[index], index, not selected] : self.flip_test_new(data))
            self.active_elements[index].grid(row = row, column = column)

        else:
            delete_index = 0
            for i in range(len(self.selected_elements)):
                if self.selected_elements[i][0].name == word.name:
                    delete_index = i
                    break

            del self.selected_elements[delete_index]
            print(len(self.selected_elements))
            self.active_elements[index].grid_forget()
            self.active_elements[index] = Button(self.game_canvas, bg = flipped_up, \
                                                text = button_text, font = self.app_font, command=lambda \
                                                data = [row, column, self.word_list_active[index], index, \
                                                not selected] : self.flip_test_new(data))
            self.active_elements[index].grid(row = row, column = column)

    def submit(self):
        if len(self.selected_elements) == 5:
            self.answers[self.goal_word] = self.selected_elements
            for element in self.selected_elements:
                word = element[0]
                index = element[1]
                row = element[2]
                column = element[3]
                button_text = '{:^25}'.format("\n%s\n" %word.name)
                self.active_elements[index].grid_forget()
                self.active_elements[index] = Button(self.game_canvas, bg = flipped_up, \
                                                    text = button_text, font = self.app_font, command=lambda \
                                                    data = [row, column, self.word_list_active[index], index, \
                                                    False] : self.flip_test_new(data))
                self.active_elements[index].grid(row = row, column = column)
            self.selected_elements = []
            index_of_word = self.word_cat_list.index(self.goal_word)
            self.category_index+=1
            if self.category_index == len(self.word_cat_list)-1:
                button_text = '{:^10}'.format("\nSee final score\n")
                self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                                    command=lambda : self.score()))
                self.sideboard_elements[-1].grid(row = 8, column = len(self.word_cat_list)//2, columnspan = len(self.word_cat_list)//2)
            else:
                self.goal_word = self.word_cat_list[self.category_index]
                self.goal_word_var.set("Find words that rhyme with %s" %self.goal_word.name)
                audio_string = "../assets/audio/findwords.mp3,../assets/audio/%s.mp3" %self.goal_word
                thread = threading.Thread(target = self.enqueue_soundfiles, \
                                            args = (audio_string,))
                thread.start()

        elif len(self.selected_elements) > 5:
            self.notification_string.set("You have too many words selected!")
            # audio queues
        elif len(self.selected_elements) < 5:
            diff = 5- len(self.selected_elements)
            self.notification_string.set("Select %i more words" %diff)

    def score(self):
        self.reset_grid()
        score = len(self.answers.keys())*5
        correct = 0
        count = 0
        for key in self.answers.keys():
            local_correct = 0
            these_answers = []
            print(key)
            for word in self.answers[key]:
                these_answers.append(word[0].name)
                if word[0] == key:
                    local_correct += 1
            correct+= local_correct
            string = "Out of %i choices you found %i words that rhyme with %s" %(5, local_correct, key)
            self.sideboard_elements.append(Label(self.game_canvas, bg = flipped_up, text = string, font = self.app_font))
            self.sideboard_elements[-1].grid(row = count, column = 0)
            count += 1
            answer_string = ", ".join(these_answers)
            string = "You selected: %s" %answer_string
            self.sideboard_elements.append(Label(self.game_canvas, bg = flipped_up, text = string, font = self.app_font))
            self.sideboard_elements[-1].grid(row = count, column = 0)
            count += 1
        string = "Overall, you scored %i/%i" %(correct, score)
        self.sideboard_elements.append(Label(self.game_canvas, bg = flipped_up, text = string, font = self.app_font))
        self.sideboard_elements[-1].grid(row = count+1, column = 0)
        count += 1
        button_text = '{:^10}'.format("\nBack to Main Menu\n")

        self.sideboard_elements.append(Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = count+2, column = 0)

    def create_board_teach(self, category_number):
        self.reset_grid()
        self.complete = 0

        index = 0
        length = 6
        width = category_number
        self.word_cat_list = []
        self.word_list_active = []
        self.word_set = set()
        while len(self.word_set) != category_number:
            rand_index = int(RNG()*len(self.word_categories))
            self.word_set.add(rand_index)

        for index in self.word_set:
            self.word_cat_list.append(self.word_categories[index])
            for key in self.word_map[self.word_categories[index].phoneme_seq]:
                self.word_list_active.append(key)

        self.word_list_active = self.shuffle(self.word_list_active)
        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()

        for i in range(len(self.word_cat_list)):
            self.sideboard_columns[self.word_cat_list[i].name] = i
            self.sideboard_map[self.word_cat_list[i].name] = 2
            button_text = '{:^10}'.format("%s" %self.word_cat_list[i].name)
            self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
            self.sideboard_elements[-1].grid(row = 0, column = i)
        index = 0
        for i in range(length):
            for j in range(width):
                self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = self.global_hidden, font = self.app_font,\
                    command=lambda data = [i, j, self.word_list_active[index], index, True] : self.flip(data)))
                self.active_elements[-1].grid(row = i, column = j)
                index += 1

    def flip(self, data):
        row = data[0]
        column = data[1]
        word = data[2]
        index = data[3]
        is_face_down = data[4]

        if len(self.selected_elements) == 2:
            if self.check_match():
                self.clear_element(0)
                self.clear_element(1)
            else:
                self.switch_state(self.selected_elements[0][1], False,\
                    self.selected_elements[0][0], self.selected_elements[0][2], \
                    self.selected_elements[0][3])
                self.switch_state(self.selected_elements[1][1], False,\
                    self.selected_elements[1][0], self.selected_elements[1][2], \
                    self.selected_elements[1][3])
            if (word, index, row, column) in self.selected_elements:
                self.selected_elements = []
                return
            self.selected_elements = []

        if is_face_down:
            audio_string = "../assets/audio/matching/%s.mp3" %word
            thread = threading.Thread(target = self.enqueue_soundfiles, \
                                        args = (audio_string,))
            thread.start()
            self.switch_state(index, is_face_down, word, row, column)
            if len(self.selected_elements) == 1:
                self.selected_elements.append((word, index, row, column))
                is_match = self.check_match()
                if is_match: #two selected elements match
                    self.set_correct_or_incorrect(self.selected_elements[1][1], False,\
                        word, row, column, correct)
                    self.set_correct_or_incorrect(self.selected_elements[0][1], False,\
                        self.selected_elements[0][0], self.selected_elements[0][2], \
                        self.selected_elements[0][3], correct)
                    goal_word = ""

                    for t_word in self.word_cat_list:
                        if t_word == word:
                            goal_word = t_word
                            break
                    button_text = '{:^10}'.format("%s" %word)
                    audio_string = "../assets/audio/wordsrhymewith.mp3,../assets/audio/matching/%s.mp3,../assets/audio/correct_tone1.mp3" %goal_word
                    print(audio_string)
                    thread = threading.Thread(target = self.enqueue_soundfiles, \
                                                args = (audio_string,))
                    thread.start()
                    self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
                    self.sideboard_elements[-1].grid(row = self.sideboard_map[goal_word.name], column = self.sideboard_columns[goal_word.name])
                    self.sideboard_map[goal_word.name] +=1
                    button_text = '{:^10}'.format("%s" %self.selected_elements[0][0])
                    self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
                    self.sideboard_elements[-1].grid(row = self.sideboard_map[goal_word.name], column = self.sideboard_columns[goal_word.name])
                    self.sideboard_map[goal_word.name] +=1

                    self.complete += 2
                    if self.complete == len(self.word_list_active):
                        audio_string = "../assets/audio/allcorrect.mp3"
                        thread = threading.Thread(target = self.enqueue_soundfiles, \
                                                    args = (audio_string,))
                        thread.start()
                        button_text = '{:^10}'.format("\nBack to Main Menu\n")
                        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                                            command=lambda : self.main_menu()))
                        self.sideboard_elements[-1].grid(row = 8, column = 0, columnspan = 6)
                        #self.reset_grid()
                        #self.build_excercise_options()
                else: # two selected elements do not match # mark
                    audio_string = "../assets/audio/incorrect_tone1.mp3,../assets/audio/wordsdontrhyme.mp3"
                    thread = threading.Thread(target = self.enqueue_soundfiles, \
                                                args = (audio_string,))
                    #timer.sleep(1)
                    thread.start()
                    self.set_correct_or_incorrect(self.selected_elements[1][1], False,\
                        word, row, column, incorrect)
                    self.set_correct_or_incorrect(self.selected_elements[0][1], False,\
                        self.selected_elements[0][0], self.selected_elements[0][2], \
                        self.selected_elements[0][3], incorrect)
            else:
                self.selected_elements.append((word, index, row, column))

        else:
            self.switch_state(index, is_face_down, word, row, column)
            del self.selected_elements[-1]

    def set_correct_or_incorrect(self, index, is_face_down, word, row, column, color):
        self.active_elements[index].grid_forget()
        string_text = '{:^20}'.format("\n%s\n" %word.name)
        self.active_elements[index]=Button(self.game_canvas, bg = color, \
            text = string_text, font = self.app_font,\
            command=lambda data = [row, column, word, index, is_face_down] : self.flip(data))
        self.active_elements[index].grid(row = row, column = column)

    def switch_state(self, index, is_face_down, word, row, column):
        if is_face_down:
            bg_color = flipped_up
            string_text = '{:^20}'.format("\n%s\n" %word.name)
            is_face_down = False
        else:
            bg_color = flipped_down
            string_text = self.global_hidden
            is_face_down = True

        self.active_elements[index].grid_forget()
        self.active_elements[index]=Button(self.game_canvas,bg = bg_color, text = string_text, font = self.app_font,\
            command=lambda data = [row, column, word, index, is_face_down] : self.flip(data))
        self.active_elements[index].grid(row = row, column = column)

    def main_menu(self):
        self.reset_grid()
        self.build_excercise_options()


    def clear_element(self, index):
        word = self.selected_elements[index][0]
        index1 = self.selected_elements[index][1]
        row1 = self.selected_elements[index][2]
        col1 = self.selected_elements[index][3]
        print("Deleting %i with word %s" %(index1, word))

        self.active_elements[index1].grid_forget()
        self.active_elements[index1] = Label(self.game_canvas, bg = inactive, text = self.global_hidden, font = self.app_font)
        self.active_elements[index1].grid(row = row1, column = col1)

    def check_match(self):
        word1 = self.selected_elements[0][0]
        word2 = self.selected_elements[1][0]
        is_match = False
        if word1 == word2:
            is_match = True
        return is_match

    def shuffle(self, local_list):
        length_local_list = len(local_list)
        for i in range(length_local_list):
            random_ind1 = int(RNG()*length_local_list)
            temp = local_list[random_ind1]
            local_list[random_ind1] = local_list[i]
            local_list[i] = temp
        return local_list

    def reset_grid(self):
        #this will not work with jagged arrays!
        if len(self.active_elements) > 0:
            for i in range(len(self.active_elements)):
                self.active_elements[i].grid_forget()
        if len(self.active_sideboard_elements) > 0:
            for i in range(len(self.active_sideboard_elements)):
                self.active_sideboard_elements[i].grid_forget()
        if len(self.sideboard_elements) > 0:
            for i in range(len(self.sideboard_elements)):
                self.sideboard_elements[i].grid_forget()
        self.active_elements = []
        self.active_sideboard_elements = []
        self.sideboard_elements = []
        self.selected_elements = []

    def clear_element_list(self, element_list):
        if len(element_list) > 0:
            for i in range(len(element_list)):
                element_list[i].grid_forget()
        element_list = []

    def enqueue_soundfiles(self, soundfile_string):
        soundfile_arr = soundfile_string.split(",")
        if(q.qsize() < max_queue_size):
            for soundfile in soundfile_arr:
                q.put(soundfile)
    """
    def play_two_clips_old(self, soundfile_string):
        soundfile_arr = soundfile_string.split(",")
        print("Soundfile: %s" %soundfile_string)
        while mixer.music.get_busy()>0:
            pass
        lock.acquire()
        for soundfile in soundfile_arr:
            # q.put(soundfile)
            mixer.music.load(soundfile)
        mixer.music.play()
        lock.release()
        mixer.music.queue(soundfile)
        while mixer.music.get_busy()>0:
            pass
    """



if __name__=='__main__':
    Game()
