from word2 import *
from collections import defaultdict
from tkinter import *
from tkinter import font, ttk
from PIL import Image, ImageTk
from random import random as RNG
from pygame import mixer
import threading, queue, os, copy, time
from resizingwindows import VertAndHorizScrolledFrame
"""
Verbal instruction about the
game we're going to look for words that rhyme
Words that rhyme sound the same at the end

Switch to single entry box,
move boxes below the header words

Notes:
Login, difficulty level
Finite number of exercises each login
Logout requires one testing
Three teaching exercises -> one test exercise at the same level as teaching
Successful (Grade of 100) test moves player to the next level

Need a case to check if student types a word under the correct column,
but doesn't click
the word for that column
you typed the word in the wrong column

You didn't didn't type word1 under the word it rhymes with
word1 word1 rhyme - word2 word2 rhyme
Turn the tile red

if word is spelled incorrectly - turn entry box red

if a word is written under the correct column but the incorrect button is clicked
You didn't click the correct rhymes - turn clicked button red

if you get it right, turn the button and entered word in the sideboard green

change main menu color
correct and incorrect chimes

listen for an enter keystroke -> if enter, play directions again

Progress bar

Making tests shorter?
"""

"""
gamedat structure
completed
pass
verbose logging
level
"""

"""
Sorting teach
hint buttons play the same hint queues,
no short I, long I sounds in the sorting teach/test

different values for the desired number of words to select
Change test and teach prompts for exercises 2 and 3 to give correct prompt
2: Click the word with the same spelling pattern as the word you typed in
3: Click the word with the same spelling pattern and vowel sound as the word you typed in

sorting test:
Player can submit empty string, and click submit again

"""

background = "#294777"
flipped_up = "#55a0d6"
flipped_down = "#ed9f47"
inactive = "#294777"
incorrect = "#ef5656"
green = "#38ea85"
colors = ["#f48042", "#caf441", "#41f4ac", "#41d0f4", "#4170f4", "#7f41f4", "#f44182", "#a81900"]

#global time_up
#global time_left
#time_up = False


q = queue.Queue()
timer_queue = queue.Queue()
max_queue_size = 20
def worker():
    print("Worker spawned")
    while True:
        if not q.empty():
            soundfile = q.get()
            print(soundfile)
            if soundfile is not None and os.path.isfile(soundfile):

                mixer.music.load(soundfile)
                mixer.music.play()
                while mixer.music.get_busy()>0:
                    pass
                #time.sleep(1)
            elif soundfile is None:
                break
            q.task_done()

class Game():
    # global time_up
    default_test_time = 300
    default_teach_time = 600
    def __init__(self, _exercise, _level):

        print("Created new instance of game")
        self.word_map = defaultdict(list)
        self.game_dat = dict()
        self.word_list = []
        self.word_categories = []
        self.active_elements = []
        self.selected_elements = []
        self.sideboard_elements = []
        self.active_sideboard_elements = []
        self.button_choices = []
        self.sound_buttons = []
        self.images = []
        self.sequence_keys = []
        self.entry_item = None
        self.progress = None
        self.UI = {}
        self.UI["notification"] = None
        self.exercise = _exercise
        self.hints_active = False
        self.attempts = 0

        mixer.init()
        # time_up = False
        self.level = 0
        self.time_left = 0
        self.teach_time = 0
        self.test_time = 0
        self.total_time = 0
        self.start_time = 0
        self.goal_word = ""
        self.global_hidden = '{:^20}'.format("\n~\n")
        with open('../datafiles/game2words_v20.txt') as infile:
            for line in infile:
                split_line = line.split()
                new_word = Word(split_line[0], split_line[1], split_line[2], split_line[3])
                self.word_map[new_word.phoneme].append(new_word)
                self.word_map[new_word.spelling_pattern].append(new_word)
                self.word_map[new_word.word] = new_word
                if new_word.phoneme not in self.sequence_keys:
                    self.sequence_keys.append(new_word.phoneme)
                if new_word.spelling_pattern not in self.sequence_keys:
                    self.sequence_keys.append(new_word.spelling_pattern)
        if os.path.isfile('../datafiles/config'):
            with open('../datafiles/config') as infile:
                for line in infile:
                    if "#" in line:
                        continue
                    split_line = line.replace(" ", "")
                    if self.teach_time == 0:
                        try:
                            self.teach_time = int(split_line)
                        except:
                            self.teach_time = default_teach_time
                    elif self.test_time == 0:
                        try:
                            self.test_time = int(split_line)
                        except:
                            self.test_time = default_test_time
                        break
        else:
            self.test_time = default_test_time
            self.teach_time = default_teach_time
        print("Read config file, set test time to %s and teach time to %s" %(self.test_time, self.teach_time))

        self.build_root()

        filename = "../assets/sound_icon.png"
        img = Image.open(filename).resize((30, 30), Image.ANTIALIAS)
        letterImg = ImageTk.PhotoImage(img)
        self.images = letterImg
        self.build_exercise(_exercise, _level)

        t = threading.Thread(target=worker)
        t.start()

        self.root.mainloop()
        q.put(None)

    def build_exercise(self, exercise, level):
        pass

    def build_root(self):
        print("Rendering Root")
        self.root = Tk()
        self.root.title('Wordification')
        text3 = "Wordification® - Version 1"

        self.root.configure(background=background)
        self.game_canvas = Canvas(self.root, bg =background)

        self.app_font = font.Font(family = "Consolas",size=14, weight='bold')
        Label(self.root, text=text3, bg =background, font = self.app_font).pack(fill=Y, side=BOTTOM, expand=FALSE)

        self.game_canvas.pack()

    # changes BG color of entry box


    def mark_box_button(self, index, color, word):
        self.button_choices[index].grid_forget()

        self.button_choices[index] = Button(self.game_canvas, \
                                            bg = color,
                                            text = '{:^15}'.format(self.example_words[index].word),
                                            font = self.app_font,\
                                            command=lambda \
                                            data = [index, self.target_patterns[index]] :\
                                            self.submit_teach(data))

        self.button_choices[index].grid(row = 6, column = index)

    def mark_box_button_2(self, index, color, word):
        j = 3
        if index // 3 == 1:
            j += 1
        self.button_choices[index].grid_forget()
        self.button_choices[index] = Button(self.game_canvas, \
                                            bg = color,
                                            text = '{:^15}'.format(self.graphemes[index]),
                                            font = self.app_font,\
                                            command=lambda \
                                            data = [index, self.graphemes[index]] :\
                                            self.submit_teach2(data))
        self.button_choices[index].grid(row = j, column = index % 3)

    def play_again(self, data):
        if data == None:
            data = "../assets/audio/matching/%s.mp3" %self.words_active[self.counter]
        if data == 'instructions':
            word = self.words_active[self.counter]
            sounds = self.words_active[self.counter].sounds.split("|")
            print(sounds)
            audio_string1 = "../assets/newAudio/Phrases/introvsound.mp3, \
                            ../assets/newAudio/Words/%s.mp3, \
                            ../assets/newAudio/Phrases/introsentence.mp3, \
                            ../assets/newAudio/Words/%s.mp3, \
                            ../assets/newAudio/Sentences/%s_sentence.mp3, \
                            ../assets/newAudio/Phrases/introsounds.mp3, \
                            ../assets/newAudio/Words/%s.mp3, \
                            ../assets/newAudio/Phrases/are2.mp3,"  %(word, word, word, word)
            audio_string2 = ""
            for sound in sounds:
                audio_string2 += "../assets/newAudio/Sounds/" + sound + ".mp3,"
            audio_string3 = "../assets/newAudio/Phrases/introvsoundselect.mp3, \
                            ../assets/newAudio/Words/%s.mp3" %(word)
            audio_string = audio_string1 + audio_string2 + audio_string3
            self.enqueue_soundfiles(audio_string)
        if mixer.music.get_busy() == 0:
            self.enqueue_soundfiles(data)

    def shuffle(self, local_s):
        length_local_s = len(local_s)
        for i in range(length_local_s):
            random_ind1 = int(RNG()*length_local_s)
            temp = local_s[random_ind1]
            local_s[random_ind1] = local_s[i]
            local_s[i] = temp
        return local_s

    def reset_grid(self):
        #this will not work with jagged arrays!
        if len(self.active_elements) > 0:
            for i in range(len(self.active_elements)):
                self.active_elements[i].grid_forget()
        if len(self.active_sideboard_elements) > 0:
            for key in self.active_sideboard_elements.keys():
                for i in range(len(self.active_sideboard_elements[key])):
                    self.active_sideboard_elements[key][i].grid_forget()
        if len(self.sideboard_elements) > 0:
            for i in range(len(self.sideboard_elements)):
                self.sideboard_elements[i].grid_forget()
        if len(self.button_choices) > 0:
            for i in range(len(self.button_choices)):
                self.button_choices[i].grid_forget()
        if len(self.sound_buttons) > 0:
            for i in range(len(self.sound_buttons)):
                self.sound_buttons[i].grid_forget()

        if self.entry_item is not None:
            self.entry_item.grid_forget()
        if self.progress is not None:
            self.progress.grid_forget()
        if self.UI["notification"] is not None:
            self.UI["notification"].grid_forget()

        self.active_elements = []
        self.active_sideboard_elements = []
        self.sideboard_elements = []
        self.selected_elements = []
        self.entry_item = None
        self.hints_active = False
        self.target_patterns = []
        self.words_active = []
        self.marked_buttons = []
        self.marked_entries = []

    def clear_elements(self, elements):
        if len(elements) > 0:
            for i in range(len(elements)):
                elements[i].grid_forget()
        elements = []

    def generate_word_list(self, words_to_generate, category):
        generated_words = []
        word_map_category_copy = copy.deepcopy(self.word_map[category])
        for i in range(words_to_generate):
            rand_index = int(RNG()*len(word_map_category_copy))
            generated_words.append(word_map_category_copy[rand_index])
            del word_map_category_copy[rand_index]
        return generated_words

    def get_random_word_from_category(self, phoneme):
        # index into wordmap by phoneme
        for word in self.word_map[phoneme]:
            if word not in self.words_active:
                return word

    def enqueue_soundfiles(self, soundfile_string):
        soundfile_arr = soundfile_string.split(",")
        print("Queueing")
        if(q.qsize() < max_queue_size):
            for soundfile in soundfile_arr:
                # print(soundfile)
                q.put(soundfile.replace(" ", ""))

    def main_menu(self):
        #self.reset_grid()
        self.root.destroy()

    def quit(self):
        self.root.destroy()

    def get_gamedat(self):
        return self.game_dat

    def time_up(self):
        self.time_left = time.clock() - self.start_time
        return False #self.time_left > self.total_time
