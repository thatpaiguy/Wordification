from word2 import *
from collections import defaultdict
from tkinter import *
from tkinter import font, ttk
from PIL import Image, ImageTk
from random import random as RNG
import time
from pygame import mixer
import threading
import queue
import os
from resizingwindows import VertAndHorizScrolledFrame
from game import Game
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

class SortingGame(Game):

    def __init__(self, _exercise, _level):
        super().__init__(_exercise, _level)

    def build_root(self):
        super().build_root()
        self.root.title('Wordification - Sorting')

    def build_exercise(self, exercise, level):
        super().build_exercise(exercise, level)
        self.level = int(level)
        test_time = self.test_time
        teach_time = self.teach_time

        self.game_dat["exercise_type"] = "Sorting"
        self.game_dat["exercise_level"] = self.level
        self.game_dat["category"] = exercise
        print(exercise)
        self.start_time = time.time()
        if exercise == "Teach":
            self.total_time = teach_time
            self.create_board_teach()

        elif exercise == "Test":
            self.total_time = test_time
            self.create_board_test()

        else: print("something went wrong")

    def init_board_variables(self):
        print("Initilizing board variables")
        self.reset_grid()
        # tracks which boxes and buttons are marked as incorrect
        self.marked_buttons = []
        self.marked_entries = []
        self.counter = 0
        self.category_number = 4
        self.width = self.category_number
        #tracks the last row to be added to sideboard
        self.sideboard_map = defaultdict()

        # tracks index of last row a word was appended to in the sideboard
        self.last_word = defaultdict()

        # list of all words shown in the sideboard
        self.active_sideboard_elements = defaultdict(list)
        self.goal_word = StringVar()
        self.goal_word_var = StringVar()
        self.categories = self.level + 1
        self.example_words = []
        self.graphemes = ['oa', 'ow', 'oCe', 'igh', 'y', 'iCe']
        self.attempts = 0
        if self.level == 1:

            self.target_patterns = ["49", "53"]
            self.partner_vowel_sounds = ["iCe", "igh", "y"]
            target_word_count = 9
            partner_vowel_count = 3
            self.example_words = [Word("long I", "49", "-", "-"),Word("long O", "53", "-", "-")]

            for seq in self.target_patterns:
                self.sideboard_map[seq] = 6
            self.target_word_list = self.generate_word_list(target_word_count, self.target_patterns[1])

            for vowel_sound in self.partner_vowel_sounds:
                self.partner_word_list = self.generate_word_list(partner_vowel_count, vowel_sound)
                for word in self.partner_word_list:

                    self.words_active.append(word)

            for word in self.target_word_list:
                self.words_active.append(word)

        elif self.level == 2 or self.level == 3:
            if self.level == 2:
                self.target_patterns = ["iCe", "igh", "y"]

                if self.exercise == "Test":
                    target_word_count = 5
                else:
                    target_word_count = 7
            elif self.level == 3:
                self.target_patterns = ["i", "iCe", "igh", "y"]
                if self.exercise == "Test":
                    target_word_count = 5
                else:
                    target_word_count = 6
            for seq in self.target_patterns:
                self.sideboard_map[seq] = 6
                self.partner_word_list = self.generate_word_list(target_word_count, seq)
                for word in self.partner_word_list:
                    self.words_active.append(word)
                    print(word.phoneme)
                self.example_words.append(self.words_active[-1])
                del self.words_active[-1]

        self.words_active = self.shuffle(self.words_active)
        self.goal_word = self.words_active[self.counter]
        self.goal_word_var.set(self.goal_word.word)

    def init_testing_variables(self):
        self.player_input = []
        self.correct_attempts = 0


    def draw_board_elements(self):
        # load progress bar
        self.progress=ttk.Progressbar(self.game_canvas,orient=HORIZONTAL,length=100*self.width,mode='determinate')
        self.progress['maximum'] = 100
        self.progress.grid(row = 2, column = 0, columnspan = self.width)

        # Instruction label, determined by exercise type
        activity_instructions = ""
        if self.exercise == "Teach":
            activity_instructions = "Click the correct vowel sound."
            self.active_elements.append(Button(self.game_canvas, \
                            bg = green, text = "Play Again",\
                            font = self.app_font, \
                            command = lambda : self.play_again(data = "instructions")))
        self.active_elements[-1].grid(row = 1, column = self.category_number)


        self.active_elements.append(Label(self.game_canvas, \
            bg = green, text = activity_instructions, font = self.app_font))
        self.active_elements[-1].grid(row = 1, column = 0, columnspan = self.width)


        #entry box to spell word
        '''
        self.entry_item = Entry(self.game_canvas, font = self.app_font)
        self.entry_item.grid(row = 3, column = 0, columnspan = self.category_number)
        '''

        # render button to check spelling of word before progressing
        '''
        self.active_elements.append(Button(self.game_canvas, \
            bg = flipped_down, font = self.app_font))
        if self.exercise == "Test":
            self.active_elements[-1].configure(
                text = '{:^10}'.format("Submit"),
                command = self.show_sounds)
        elif self.exercise == "Teach":
            self.active_elements[-1].configure(
                text = '{:^10}'.format("Check spelling"),
                command = self.check_spelling)
        '''
        #self.active_elements[-1].grid(row = 4, column = 0, columnspan = self.category_number)

# creates the initial teaching board
    def create_board_teach(self):
        self.init_board_variables()
        self.draw_board_elements()
        self.button_choices = []
        self.sound_buttons = []

        # for now, ignore the levels. functionality for level 1 is complete
        for i in range(self.categories):
            example_word = self.example_words[i]
            # builds board; when button is clicked, jump to submit_teach method
            self.button_choices.append(Button(self.game_canvas, \
                                                bg = flipped_down, \
                                                text = '{:^15}'.format(self.example_words[i].word), \
                                                font = self.app_font,
                                                command=lambda \
                                                data = [i,  self.target_patterns[i]] :\
                                                self.submit_teach(data)))

            example_word = self.get_random_word_from_category(self.example_words[i].phoneme)
            while example_word in self.words_active:
                example_word = self.get_random_word_from_category(self.example_words[i].phoneme)
            phone_file_name = self.example_words[i].word.replace(" ", "").lower()
            audio_string = "../assets/newAudio/Sounds/%s.mp3" %(self.example_words[i].phoneme)


            self.sound_buttons.append(Button(self.game_canvas, \
                bg = flipped_down, text = '{:^15}'.format("Hint"), font = self.app_font,\
                command=lambda data = audio_string : self.play_again(data)))

        #play instructions again
        self.show_sounds()


    # displays sounds and plays audio when clicked
    def show_sounds(self):
        #if not self.time_up() and not self.hints_active:
        self.hints_active = True
        print("Displaying sounds")
        print(range(len(self.button_choices)))
        for i in range(len(self.button_choices)):
            if len(self.sound_buttons) > 0 :
                self.sound_buttons[i].grid(row = 5, column = i)
            self.button_choices[i].grid(row = 6, column = i)

        # audio_string = "../assets/newAudio/Phrases/intro_vsound.mp3"
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
        print(audio_string)
        self.enqueue_soundfiles(audio_string)

    '''
        elif self.time_up():
            print("Going to breakdown or score from show_sounds()")
            if self.exercise == "Teach":
                # change this
                self.main_menu()
                # self.teach_breakdown()
            elif self.exercise == "Test":
                self.score()
        '''

    # accessed from the board creation,
    # sends data to check_answer
    def submit_teach(self, data):
        if not self.time_up():
            #location of button within
            index = data[0]
            word = data[1]
            self.check_answer(index, word)
        else:
            self.teach_breakdown()

    # checks if correct vowel was clicked
    # once again, only level 1 functionality is complete
    def check_answer(self, index, word):
        # check if the correct vowel was clicked
        if self.target_patterns[index] != self.goal_word.phoneme:
            # mark_box_button method can be found in game.py
            # this method is what turns the box red
            self.mark_box_button(index, incorrect, word)
            self.marked_buttons.append(index)
            # Find the incorrect phoneme that the user picked
            # from the list of target patterns (note: this logic
            # only works when the game is testing two target patterns)
            for ph in self.target_patterns:
                if ph != self.goal_word.phoneme:
                    inc_phoneme = str(ph)
            audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                            ../assets/newAudio/Sounds/%s.mp3, \
                            ../assets/newAudio/Phrases/incorrect_vsound.mp3, \
                            ../assets/newAudio/Words/%s.mp3" %(inc_phoneme, self.words_active[self.counter])
            self.enqueue_soundfiles(audio_string)
            return

        elif self.goal_word.phoneme == self.target_patterns[index]:
            # play soundfile
            audio_string = "../assets/newAudio/Phrases/correct.mp3, \
                            ../assets/newAudio/Sounds/%s.mp3, \
                            ../assets/newAudio/Phrases/correct_vsound.mp3, \
                            ../assets/newAudio/Words/%s.mp3" %(self.goal_word.phoneme, self.words_active[self.counter])
            self.enqueue_soundfiles(audio_string)
            # if answer is correct, move on to showing graphemes
            self.show_graphemes()
            return


    # shows graphemes to user
    def show_graphemes(self):
        #reset incorrectly marked boxes
        self.hints_active = False
        for i in self.marked_entries:
            self.mark_box_entry(i, "white")
        for i in self.marked_buttons:
            self.mark_box_button(i, flipped_down, self.target_patterns[i])
        self.marked_buttons = []
        self.marked_entries = []

        for i in range(self.categories):
            self.sound_buttons[i].grid_forget()
            self.button_choices[i].grid_forget()
        self.button_choices = []
        # creates each of the buttons for the grapheme board
        # when button is clicked, jumps to submit_teach_graphemes
        for i in range(len(self.graphemes)):
            print(self.graphemes[i] + ' appending')
            self.button_choices.append(
                Button(
                    self.game_canvas, \
                    bg = flipped_down, \
                    text = '{:^15}'.format(self.graphemes[i]), \
                    font = self.app_font,\
                    command=lambda \
                    data = [i, self.graphemes[i]] :\
                    self.submit_teach_graphemes(data)
                )
            )
        if not self.time_up():
            self.hints_active = True
            print("Displaying graphemes")
            j = 3
            for i in range(len(self.button_choices)):
                #if len(self.sound_buttons) > 0 :
                #    self.sound_buttons[i].grid(row = 5, column = i)
                self.button_choices[i].grid(row = j, column = i % 3)
                if i % 3 == 2:
                    j += 1

            audio_string = "../assets/newAudio/Phrases/spelling_pattern.mp3, \
                                ../assets/newAudio/Sounds/%s.mp3, \
                                ../assets/newAudio/Phrases/in.mp3, \
                                ../assets/newAudio/Words/%s.mp3" %(self.goal_word.phoneme, self.words_active[self.counter])
            self.enqueue_soundfiles(audio_string)
        elif self.time_up():
            print("Going to breakdown or score from show_graphemes()")
            if self.exercise == "Teach":
                # change this
                self.main_menu()
                # self.teach_breakdown()
            elif self.exercise == "Test":
                self.score()

    # sends info to check_graphemes to check
    # whether correct grapheme was selected
    def submit_teach_graphemes(self, data):
        self.attempts += 1
        if not self.time_up():
            #location of button within
            index = data[0]
            word = data[1]
            self.check_graphemes(index, word)
        else:
            self.teach_breakdown()

    # checks whether correct grapheme was selected
    def check_graphemes(self, index, word):
        # check if the correct vowel was clicked
        if self.level == 1 :
            if self.graphemes[index] != self.goal_word.spelling_pattern:
                print(self.graphemes[index])
                print(self.goal_word.spelling_pattern)
                self.mark_box_button_2(index, incorrect, word)
                self.marked_buttons.append(index)
                if self.attempts == 1:
                    # if index / 3 is 0, then user selected an o vowel
                    if index / 3 == 0:
                        # the user selected the correct sound, but incorrect spelling pattern
                        if self.graphemes.index(self.goal_word.spelling_pattern) / 3 == 0:
                            audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                                            ../assets/newAudio/Phrases/the.mp3, \
                                            ../assets/newAudio/Sounds/%s.mp3, \
                                            ../assets/newAudio/Phrases/in.mp3, \
                                            ../assets/newAudio/Words/%s.mp3, \
                                            ../assets/newAudio/Phrases/not_spelled_with.mp3, \
                                            ../assets/newAudio/Sounds/%s.mp3" %(self.goal_word.phoneme, self.words_active[self.counter], self.graphemes[index])
                            self.enqueue_soundfiles(audio_string)
                        # the user selected the incorrect sound and incorrect spelling pattern
                        else:
                            audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                                            ../assets/newAudio/Sounds/%s.mp3, \
                                            ../assets/newAudio/Phrases/not_spelling_pattern.mp3, \
                                            ../assets/newAudio/Words/%s.mp3, \
                                            ../assets/newAudio/Phrases/tryagain.mp3," %(self.graphemes[index], self.words_active[self.counter])
                            self.enqueue_soundfiles(audio_string)
                    # if index / 3 is 1, then user selected an i vowel
                    else:
                        # the user selected the correct sound, but incorrect spelling pattern
                        if self.graphemes.index(self.goal_word.spelling_pattern) / 3 == 1:
                            audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                                            ../assets/newAudio/Phrases/the.mp3, \
                                            ../assets/newAudio/Sounds/%s.mp3, \
                                            ../assets/newAudio/Phrases/in.mp3, \
                                            ../assets/newAudio/Words/%s.mp3, \
                                            ../assets/newAudio/Phrases/not_spelled_with.mp3, \
                                            ../assets/newAudio/Sounds/%s.mp3" %(self.goal_word.phoneme, self.words_active[self.counter], self.goal_word.spelling_pattern)
                            self.enqueue_soundfiles(audio_string)
                        # the user selected the incorrect sound and incorrect spelling pattern
                        else:
                            audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                                            ../assets/newAudio/Sounds/%s.mp3, \
                                            ../assets/newAudio/Phrases/not_spelling_pattern.mp3, \
                                            ../assets/newAudio/Words/%s.mp3, \
                                            ../assets/newAudio/Phrases/tryagain.mp3," %(self.graphemes[index], self.words_active[self.counter])
                            self.enqueue_soundfiles(audio_string)
                if self.attempts == 2:
                    audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                                    ../assets/newAudio/Phrases/the.mp3, \
                                    ../assets/newAudio/Sounds/%s.mp3, \
                                    ../assets/newAudio/Phrases/in.mp3, \
                                    ../assets/newAudio/Words/%s.mp3, \
                                    ../assets/newAudio/Phrases/spelled_with.mp3, \
                                    ../assets/newAudio/Sounds/%s.mp3" %(self.goal_word.phoneme, self.words_active[self.counter], self.goal_word.spelling_pattern)
                    self.enqueue_soundfiles(audio_string)
                    for i in range(len(self.graphemes)):
                        self.button_choices[i].grid_forget()
                    self.show_spelling()
                return

            elif self.graphemes[index] == self.goal_word.spelling_pattern:
                # play soundfile
                audio_string = "../assets/newAudio/Phrases/correct.mp3, \
                                ../assets/newAudio/Phrases/the.mp3, \
                                ../assets/newAudio/Sounds/%s.mp3, \
                                ../assets/newAudio/Phrases/in.mp3, \
                                ../assets/newAudio/Words/%s.mp3, \
                                ../assets/newAudio/Phrases/spelled_with.mp3, \
                                ../assets/newAudio/Sounds/%s.mp3" %(self.goal_word.phoneme, self.words_active[self.counter], self.goal_word.spelling_pattern)
                self.enqueue_soundfiles(audio_string)
                for i in range(len(self.graphemes)):
                    self.button_choices[i].grid_forget()
                self.show_spelling()
                return
    # creates spelling box
    def show_spelling(self):
        self.attempts = 0
        self.entry_item = Entry(self.game_canvas, font = self.app_font)
        self.entry_item.grid(row = 3, column = 0, columnspan = self.category_number)

        self.active_elements.append(Button(self.game_canvas, \
                    bg = flipped_down, font = self.app_font))
        if self.exercise == "Test":
            self.active_elements[-1].configure(
                text = '{:^10}'.format("Submit"),
                command = self.show_sounds)
        elif self.exercise == "Teach":
            self.active_elements[-1].configure(
                text = '{:^10}'.format("Check spelling"),
                command = self.check_spelling)
        self.active_elements[-1].grid(row = 4, column = 0, columnspan = self.category_number)
        audio_string = "../assets/newAudio/Phrases/box_prompt.mp3, \
                        ../assets/newAudio/Words/%s.mp3" %(self.words_active[self.counter])
        self.enqueue_soundfiles(audio_string)
    # checks box input
    def check_spelling(self):
            # wrong spelling - mark spelling box incorrect
            self.attempts += 1
            if not self.time_up():
                print("%s == %s - %s" %(self.entry_item.get(), self.words_active[self.counter],  self.entry_item.get() == self.words_active[self.counter]))
                if self.entry_item.get() != self.words_active[self.counter]:
                    if self.attempts == 1:
                        self.mark_box_entry(incorrect)
                        audio_string = "../assets/newAudio/Phrases/incorrect.mp3, \
                                        ../assets/newAudio/Words/%s.mp3, \
                                        ../assets/newAudio/Phrases/has_sound.mp3, \
                                        ../assets/newAudio/Sounds/%s.mp3, \
                                        ../assets/newAudio/Phrases/and_spelled_with.mp3, \
                                        ../assets/newAudio/Sounds/%s.mp3, \
                                        ../assets/newAudio/Phrases/tryagain.mp3" %(self.words_active[self.counter], self.goal_word.phoneme, self.goal_word.spelling_pattern)
                        self.enqueue_soundfiles(audio_string)
                    else:
                        self.mark_box_entry(incorrect)
                        audio_string1 = "../assets/newAudio/Phrases/incorrect.mp3, \
                                        ../assets/newAudio/Words/%s.mp3, \
                                        ../assets/newAudio/Phrases/is_spelled.mp3, " %(self.goal_word.phoneme)
                        audio_string2 = ""
                        letters = list(self.words_active[self.counter].word)
                        print(letters)
                        for letter in letters:
                            audio_string2 += "../assets/newAudio/Letters/" + letter + ".mp3,"
                        audio_string3 = "../assets/newAudio/Phrases/lets_look.mp3"
                        audio_string = audio_string1 + audio_string2 + audio_string3
                        self.enqueue_soundfiles(audio_string)
                        self.move_to_next_word(self.words_active[self.counter], self.counter)

                elif self.entry_item.get() == self.words_active[self.counter]: # word spelled correctly
                    self.mark_box_entry("white")
                    #self.hints_active = True
                    print("playing sounds")
                    # play right sound, "Congrats you typed the right word"
                    audio_string1 = "../assets/newAudio/Phrases/correct.mp3, \
                                    ../assets/newAudio/Words/%s.mp3, \
                                    ../assets/newAudio/Phrases/is_spelled.mp3," %(self.words_active[self.counter])
                    letters = list(self.words_active[self.counter].word)
                    audio_string2 = ""
                    for letter in letters:
                        audio_string2 += "../assets/newAudio/Letters/" + letter + ".mp3,"
                    audio_string = audio_string1 + audio_string2
                    self.enqueue_soundfiles(audio_string)
                    self.move_to_next_word(self.words_active[self.counter], self.counter)

            elif self.time_up():
                self.teach_breakdown()
    # resets all boxes and goes to next word
    def move_to_next_word(self, word, index):
        #reset incorrectly marked boxes
        self.attempts = 0
        self.hints_active = False
        for i in self.marked_entries:
            self.mark_box_entry(i, "white")
        self.marked_buttons = []
        self.marked_entries = []

        for i in range(self.categories):
            self.sound_buttons[i].grid_forget()
            self.button_choices[i].grid_forget()
        self.button_choices = []

        # move counter to next word, check if exercise is done
        self.counter += 1
        if(self.counter >= len(self.words_active)):
            self.main_menu()
            #self.teach_breakdown()
            return
        # set new goal word
        self.goal_word = self.words_active[self.counter]
        self.goal_word_var.set(self.goal_word)

        #play instructions again
        '''
        # append word to sideboard
        if(self.sideboard_map[word] > 6):
            self.active_sideboard_elements[self.target_patterns[index]][-1].grid_forget()
            self.active_sideboard_elements[self.target_patterns[index]][-1] = Label(self.game_canvas, \
                bg = flipped_down, text = '{:^20}'.format(self.last_word[index]), font = self.app_font)
            self.active_sideboard_elements[self.target_patterns[index]][-1].grid(row = self.sideboard_map[word], column = index)

        self.sideboard_map[word]+=1
        self.active_sideboard_elements[self.target_patterns[index]].append(Label(self.game_canvas, \
            bg = green, text = '{:^20}'.format(self.entry_item.get()), font = self.app_font))

        self.last_word[index] = self.entry_item.get()
        self.active_sideboard_elements[self.target_patterns[index]][-1].grid(row = self.sideboard_map[word], column = index)
        '''

        # clear entry box
        self.entry_item.grid_forget()
        self.active_elements[-1].grid_forget()
        self.progress['value']=int((self.counter/len(self.words_active))*100)

        self.button_choices = []
        for i in range(self.categories):
            example_word = self.example_words[i]
            # builds board; when button is clicked, jump to submit_teach method
            self.button_choices.append(Button(self.game_canvas, \
                                                bg = flipped_down, \
                                                text = '{:^15}'.format(self.example_words[i].word), \
                                                font = self.app_font,
                                                command=lambda \
                                                data = [i,  self.target_patterns[i]] :\
                                                self.submit_teach(data)))
            example_word = self.get_random_word_from_category(self.example_words[i].phoneme)
            while example_word in self.words_active:
                example_word = self.get_random_word_from_category(self.example_words[i].phoneme)
            phone_file_name = self.example_words[i].word.replace(" ", "").lower()
            audio_string = "../assets/newAudio/Sounds/%s.mp3" %(self.example_words[i].phoneme)

            self.sound_buttons.append(Button(self.game_canvas, \
                bg = flipped_down, text = '{:^15}'.format("Hint"), font = self.app_font,\
                command=lambda data = audio_string : self.play_again(data)))

    def teach_breakdown(self):
        timer_queue.put(None)
        self.enqueue_soundfiles("allcorrect.mp3");
        button_text = '{:^10}'.format("\nYou ran out of time!\nDon't worry, you'll do better next time!\n")
        if not self.time_up():
            timer_queue.put(None)
            time_minutes = self.time_left//60
            time_seconds = int(self.time_left) % 60
            button_text = '{:^10}'.format("Congratulations you finished with %i minutes and %i seconds left " %(time_minutes, time_seconds))
            self.game_dat["time"] = int(self.time_left)
        else:
            self.game_dat["time"] = 0

        self.game_dat["complete"] = self.counter
        self.game_dat["correct"] = 0
        self.game_dat["correct_categories"] = 0
        self.game_dat["total_words"] = len(self.words_active)
        self.game_dat["total_categories"] = ",".join(self.target_patterns)
        self.game_dat["verbose_logs"] = "NA"
        self.game_dat["passed"] = "NA"
        self.game_dat["score"] = 100.0
        self.reset_grid()
        #self.game_canvas.destroy()

        #generate main menu button
        self.active_elements.append(Label(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font))
        self.active_elements[-1].grid(row = 0, column = 0)
        button_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.main_menu_button = Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=self.main_menu)
        self.main_menu_button.grid(row = 1, column = 0)

    def create_board_test(self):
        print("in testing")
        self.init_board_variables()
        self.init_testing_variables()
        self.draw_board_elements()
        # create buttons for sorting word into categories
        self.button_choices = []

        for i in range(len(self.target_patterns)):
            self.button_choices.append(
                Button(
                    self.game_canvas, \
                    bg = flipped_down, \
                    text = '{:^15}'.format(self.example_words[i].word), \
                    font = self.app_font,\
                    command=lambda \
                    data = [i, self.target_patterns[i]] :\
                    self.submit_test(data)
                )
            )

        audio_string = "../assets/audio/spellword_sorting.mp3,../assets/audio/matching/%s.mp3" %(self.words_active[self.counter])
        self.enqueue_soundfiles(audio_string)

    def submit_test(self, data):
        print("in submit test")
        print(data)
        index = data[0]
        pattern = data[1]
        self.hints_active = False

        string = "You had to spell: %s.\nYou typed %s and said it had the same vowel sound as %s.\n" \
                    %(self.words_active[self.counter], self.entry_item.get(), pattern)
        answer = "Incorrect"
        print("counter = %s" %self.counter)
        print("words_active len = %s" %len(self.words_active))
        if self.level == 1:
            if self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme == pattern:
                string += " You were correct!"
                answer = "Correct"
                self.correct_attempts += 1

            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme == pattern:
                string += " You misspelled %s and you matched it with the correct category."

            elif self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme != pattern:
                string += " You spelled %s correctly and you didn't match it with the correct category."

            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme != pattern:
                string += " You misspelled %s and you didn't match it with the correct category."
        elif self.level == 2:
            if self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].spelling_pattern == pattern:
                string += " You were correct!"
                answer = "Correct"
                self.correct_attempts += 1
            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].spelling_pattern == pattern:
                string += " You misspelled %s, but you matched it with the correct category."
            elif self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].spelling_pattern != pattern:
                string += " You spelled %s correctly, but didn't match it with the correct category."
            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].spelling_pattern != pattern:
                string += " You spelled %s incorrectly, and didn't match it with the correct category."
        elif self.level == 3:
            if self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme == self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern == self.example_words[index].spelling_pattern:
                string += " You were correct!"
                answer = "Correct"
                self.correct_attempts += 1
            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme == self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern == self.example_words[index].spelling_pattern:
                string += " You misspelled %s, but you matched it with the correct category." %self.words_active[self.counter].word
            elif self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme != self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern == self.example_words[index].spelling_pattern:
                string += " You spelled %s correctly, matched the correct spelling pattern, but matched the wrong vowel sound." %self.words_active[self.counter].word
            elif self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme == self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern != self.example_words[index].spelling_pattern:
                string += " You spelled %s correctly, matched the correct vowel sound, but matched the wrong spelling pattern." %self.words_active[self.counter].word
            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme != self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern == self.example_words[index].spelling_pattern:
                string += " You misspelled %s, correctly, matched the correct spelling pattern, but matched the wrong vowel sound." %self.words_active[self.counter].word
            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme == self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern != self.example_words[index].spelling_pattern:
                string += " You misspelled %s, correctly, matched the correct vowel sound, but matched the wrong spelling_pattern. " %self.words_active[self.counter].word
            elif self.entry_item.get() == self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme != self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern != self.example_words[index].spelling_pattern:
                string += " You spelled %s correctly, but didn't find the correct vowel sound and spelling pattern." %self.words_active[self.counter].word
            elif self.entry_item.get() != self.words_active[self.counter].word and \
                self.words_active[self.counter].phoneme != self.example_words[index].phoneme and \
                self.words_active[self.counter].spelling_pattern != self.example_words[index].spelling_pattern:
                string += " You mispelled the word %s, and didn't find the correct vowel sound and spelling pattern." %self.words_active[self.counter].word
        self.player_input.append((answer, self.words_active[self.counter], string))
        self.counter +=1
        self.progress['value']=int((self.counter/len(self.words_active))*100)

        if(self.counter >= len(self.words_active)):
            self.score()
            return

        audio_string = "../assets/audio/spellword_sorting.mp3,../assets/audio/matching/%s.mp3" \
                        %(self.words_active[self.counter].word)
        self.enqueue_soundfiles(audio_string)
        self.entry_item.delete(0, 'end')
        for i in range(len(self.target_patterns)):
            self.button_choices[i].grid_forget()

    def mark_box_entry(self, color):
        word = self.entry_item.get()
        self.entry_item.grid_forget()
        self.entry_item = Entry(self.game_canvas, font = self.app_font, bg = color)
        self.entry_item.grid(row = 3, column = 0, columnspan = self.categories+2) #wont properly align with certain exercises
        self.entry_item.insert(0, word)

    def score(self):

        count = 0
        correct_per_category = {}
        feedback = []
        for seq in self.target_patterns:
            correct_per_category[seq] = 0
        #write to file

        for answer in self.player_input:
            is_correct = answer[0]
            word = answer[1]
            answer_verbose = answer[2]
            feedback.append(answer_verbose)
            count+=1
            if is_correct:
                if self.level == 1:
                    correct_per_category[word.phoneme] += 1
                elif self.level == 2:
                    correct_per_category[word.spelling_pattern] += 1
                elif self.level == 3:
                    correct_per_category[word.spelling_pattern] += 1
        can_move_on = True

        print("Player input length: %s" %len(self.player_input))
        print("Answer length: %s" %len(feedback))

        min_answers_correct = 8
        if self.level == 2:
            min_answers_correct = 5
        elif self.level == 3:
            min_answers_correct = 4
        correct_categories = 0
        for seq in correct_per_category.keys():
            if correct_per_category[seq] < min_answers_correct:
                can_move_on = False
                break
            else:
                correct_categories += 1
        score = (self.correct_attempts/len(self.words_active))*100

        # package game data
        if self.time_left == 0:
            self.game_dat["time"] = "0"
        else:
            self.game_dat["time"] = self.time_left
        self.game_dat["complete"] = len(self.player_input)
        self.game_dat["correct"] = self.correct_attempts
        self.game_dat["correct_categories"] = correct_categories
        self.game_dat["total_words"] = len(self.words_active)
        self.game_dat["total_categories"] = ",".join(self.target_patterns)
        self.game_dat["verbose_logs"] = feedback
        self.game_dat["passed"] = can_move_on
        self.game_dat["score"] = self.correct_attempts/len(self.words_active)

        string = "Overall, you scored a %0f (%i/%i)" %((self.correct_attempts/len(self.words_active))*100, self.correct_attempts, len(self.words_active))
        self.reset_grid()
        self.game_canvas.destroy()
        scoring_menu = VertAndHorizScrolledFrame(self.root,background)
        scoring_menu.pack()
        self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = string, font = self.app_font))
        self.sideboard_elements[-1].grid(row = 1, column = 0)
        #count += 1
        button_text = '{:^10}'.format("\nBack to Main Menu\n")

        self.sideboard_elements.append(Button(scoring_menu.interior, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 0, column = 0)
        count = 2
        if len(self.player_input) > 0 :
            for answer in feedback:
                print(answer)
                self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = answer, font = self.app_font))
                self.sideboard_elements[-1].grid(row = count, column = 0)
                count+=1
        else:
            self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = "You didn't have any answers.", font = self.app_font))
            self.sideboard_elements[-1].grid(row = count, column = 0)


if __name__=='__main__':
    SortingGame("Teach", 3)
