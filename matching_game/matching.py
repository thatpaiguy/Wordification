from word2 import *
from collections import defaultdict
from tkinter import *
from tkinter import font
from PIL import Image, ImageTk
from random import random as RNG
import time
from pygame import mixer
from game import Game
import threading, queue, os
from resizingwindows import VertAndHorizScrolledFrame
"""
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

12/18/2017
Add soundfiles to the matching test, to let players know if they have too many or
too few words selected

Stop players from selecting next words during teaching

Add colors to matching test game to make the word players are trying to find
rhyming words for more noticeable

Correct prompts for exercises 2 and 3 to match purpose of the w
Find x words that have the same spelling pattern as y word
Find x words that have the same spelling pattern and vowel sound as y word
record 4,5,6,7,8 sounds for testing
Change feedback if word is incorrect for the teach exercises
Change feedback if match is correct
"""
background = "#294777"
flipped_up = "#55a0d6"
flipped_down = "#ed9f47"
inactive = "#294777"#"#f9be7a"
incorrect = "#ef5656"
correct = "#38ea85"
color_list = ["#f48042", "#caf441", "#41f4ac", "#41d0f4", "#4170f4", "#7f41f4", "#f44182", "#a81900"]

global time_left

q = queue.Queue()
max_queue_size = 8


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
            elif soundfile is None:
                break
            q.task_done()


class MatchingGame(Game):

    def __init__(self, exercise, level):
        super().__init__(exercise, level)
        print("called init")

    def build_root(self): 
        super().build_root()
        self.root.title('Wordification - Matching')
        self.sideboard = Canvas(self.root, bg =background)
        self.sideboard.pack()

    def build_exercise(self, exercise, level):
        super().build_exercise(exercise, level)
        self.level = int(level)
        test_time = self.test_time
        teach_time = self.teach_time

        self.game_dat["exercise_type"] = "Matching"
        self.game_dat["exercise_level"] = self.level
        self.game_dat["category"] = exercise
        print(exercise)
        if exercise == "Teach":
            self.total_time = teach_time
            self.start_time = time.clock()
            # t = threading.Thread(target=timer, args = (teach_time,))
            # t.start()            
            if level == 1: self.create_board_teach_level1()
            elif level == 2: self.create_board_teach_level2()
            elif level == 3: self.create_board_teach_level3()
        elif exercise == "Test":
            self.total_time = test_time
            self.start_time = time.clock()
            # t = threading.Thread(target=timer, args = (test_time,))
            # t.start()
            print("called test")
            self.create_board_test()
    
    def create_board_test(self):
        self.reset_grid()
        print("called test")
        self.complete = 0
        index = 0
        length = 4
        width = 6
        distractor_count = 6
        # type Word = list of all active words in the game
        self.words_active = []

        # self.active_incorrect = []
        # type Word - list of all actively selected words
        self.selected_elements = []

        # type Word - list of two sample words players find rhymes for
        self.example_words = []

        self.word_set = set()

        self.goal_word_var = StringVar()
        self.button_text = StringVar()
        self.notification_string = StringVar()

        self.answers = defaultdict(list)
        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()
        self.active_sideboard_elements = defaultdict(list)
        self.category_index = 0
        if self.level == 1:
            self.test_excercise_target_words_per_category = 8
            self.goal_word_var.set("Find %i words that have the same vowel sound as" %self.test_excercise_target_words_per_category)
                    # This would be determined randomly in the production version of the game
            self.target_word_phoneme = "40"
            self.partner_phoneme = "49"
            self.target_patterns = [self.target_word_phoneme, self.partner_phoneme]
            self.example_words = []

            self.partner_graphemes = ["iCe", "igh", "y"]

            # set number of words to be generated from each category
            target_word_count = 10
            partner_vowel_count = 3     

            # load distractor words
            self.distractor_category = self.load_distractor_words(distractor_count, self.target_patterns)

            #generate list of indices corresponding to words that contain the targeted word phoneme
            self.target_word_set = self.generate_word_set(target_word_count, self.target_word_phoneme)

            #populate list of words with the same vowel sounds but different phonemes
            for vowel_sound in self.partner_graphemes:
                self.partner_word_set = self.generate_word_set(partner_vowel_count, vowel_sound)
                print("Generated word %s set" % vowel_sound)
                for index in self.partner_word_set:
                    self.words_active.append(self.word_map[vowel_sound][index])

            #randomly generate a word from one partner phoneme categories to be set as rhyming goal words
            rand_ind = int(RNG()*len(self.partner_graphemes))
            rand_ind2 = int(RNG()*len(self.word_map[self.partner_graphemes[rand_ind]]))
            while self.word_map[self.partner_graphemes[rand_ind]][rand_ind2] in self.words_active :
                print("Generating example words")
                rand_ind = int(RNG()*len(self.partner_graphemes))
                rand_ind2 = int(RNG()*len(self.word_map[self.partner_graphemes[rand_ind]]))
            print("Finished generating example word")
            self.example_words.append(self.word_map[self.partner_graphemes[rand_ind]][rand_ind2])

            #populate active list with words that contain the target phoneme seq
            for index in self.target_word_set:
                self.words_active.append(self.word_map[self.target_word_phoneme][index])

            self.example_words.append(self.words_active[-1])
            del self.words_active[-1]

            audio_string = "../assets/audio/matching_test_instructions_p1_level1.mp3,../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]
        elif self.level == 2:
            self.test_excercise_target_words_per_category = 6
            
            self.goal_word_var.set("Find %i words that have the same spelling pattern as " %self.test_excercise_target_words_per_category)
            self.categories = 4
            self.target_patterns = ["iCe", "igh", "y"]
            self.example_words = []
            target_word_count = 7

            for seq in self.target_patterns:
                self.sideboard_map[seq] = 6
                self.partner_word_set = self.generate_word_set(target_word_count, seq)
                for index in self.partner_word_set:
                    self.words_active.append(self.word_map[seq][index])
                self.example_words.append(self.words_active[-1])
                del self.words_active[-1]
            audio_string = "../assets/audio/matching_test_instructions_p1_level2.mp3,../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]
        # load distractor words
        
        elif self.level == 3:
            self.test_excercise_target_words_per_category = 6
            self.goal_word_var.set("Find %i words that have the same vowel sound and spelling pattern as" %self.test_excercise_target_words_per_category)
            length = 5
            self.categories = 4
            self.target_patterns = ["40", "iCe", "igh", "y"]
            self.example_words = []
            target_word_count = 7

            for seq in self.target_patterns:
                self.sideboard_map[seq] = 6
                self.partner_word_set = self.generate_word_set(target_word_count, seq)
                for index in self.partner_word_set:
                    self.words_active.append(self.word_map[seq][index])
                self.example_words.append(self.words_active[-1])
                del self.words_active[-1]
            audio_string = "../assets/audio/matching_test_instructions_p1_level3.mp3,../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]

        self.distractor_category = self.load_distractor_words(distractor_count, self.target_patterns)
        for word in self.distractor_category:
            self.words_active.append(word)

        self.words_active = self.shuffle(self.words_active)

        # generate instruction label
       
        self.sideboard_elements.append(Label(self.sideboard, bg = flipped_down, textvariable = self.goal_word_var, font = self.app_font))
        self.sideboard_elements[-1].grid(row = 0, column = 0, columnspan = 3*width//4)

        #generate play again button for the current goal word
        self.button_text.set('{:^5}'.format("%s" %self.example_words[self.category_index]))
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, textvariable = self.button_text, font = self.app_font,\
                                            command=lambda: self.play_again(data = None)))
        self.sideboard_elements[-1].grid(row = 0, column = 3*width//4, columnspan = 1*width//4)

        #generate submission button
        button_text = '{:^10}'.format("\nConfirm Selection\n")
        self.selection_confirmation_button = Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command = self.submit)
        self.selection_confirmation_button.grid(row = 8, column = 0, columnspan = width//2)

        #generate column labels for vowel types being tested
        for i in range(len(self.example_words)):
            self.sideboard_columns[self.example_words[i].word] = i
            button_text = '{:^10}'.format("%s" %self.example_words[i])
            self.sideboard_elements.append(Label(self.sideboard, bg = color_list[i], text = button_text, font = self.app_font))
            self.sideboard_elements[-1].grid(row = 1, column = i)
        index = 0

        #populate board with cards
        for i in range(length):
            for j in range(width):
                button_text = '{:^25}'.format("\n%s\n" %self.words_active[index])
                self.active_elements.append(Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                    command=lambda data = [i, j, self.words_active[index], index, False] : self.flip_test(data)))
                self.active_elements[-1].grid(row = i, column = j)
                index += 1


        self.enqueue_soundfiles(audio_string)
        for pattern in self.example_words:
            self.answers[pattern.word] = []

    def submit(self):
        # if player selected right number of cards
        print("Called submit")
        length = 4
        if len(self.words_active) == 30:
            length = 5
        width = 6
        if len(self.selected_elements) == self.test_excercise_target_words_per_category or self.time_up():
            self.answers[self.example_words[self.category_index].word] = self.selected_elements
            self.selected_elements = []
            self.category_index += 1

            if self.category_index < len(self.example_words) and not self.time_up():
                if self.level == 1:
                    audio_string = "../assets/audio/matching_test_instructions_p1_level1.mp3,../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]
                elif self.level == 2:
                    audio_string = "../assets/audio/matching_test_instructions_p1_level2.mp3,../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]
                elif self.level == 3:
                    audio_string = "../assets/audio/matching_test_instructions_p1_level3.mp3,../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]
                thread = threading.Thread(target = self.enqueue_soundfiles, \
                                            args = (audio_string,))
                thread.start()
                self.button_text.set('{:^5}'.format("%s" %self.example_words[self.category_index]))
                #shuffle board
                index = 0
                self.words_active = self.shuffle(self.words_active)
                for i in range(length):
                    for j in range(width):
                        self.active_elements[index].grid_forget()
                        button_text = '{:^25}'.format("\n%s\n" %self.words_active[index])
                        self.active_elements[index] = Button(self.game_canvas, bg = flipped_up, text = button_text, font = self.app_font,\
                            command=lambda data = [i, j, self.words_active[index], index, False] : self.flip_test(data))
                        self.active_elements[index].grid(row = i, column = j)
                        index += 1
                if self.UI["notification"] != None:
                    self.UI["notification"].grid_forget()

            elif self.category_index >= len(self.example_words) or self.time_up():
                print("Time up")
                """
                button_text = '{:^10}'.format("\nYou ran out of time!\nDon't worry, you'll do better next time!\n")
                
                print(self.time_left)
                if self.time_left > 0:
                    time_minutes = self.time_left//60
                    time_seconds = int(self.time_left) % 60
                    button_text = '{:^10}'.format("Congratulations, you finished with %i minutes and %i seconds left " %(time_minutes, time_seconds))
                for element in self.active_elements:
                    element.grid_forget()
                for element in self.sideboard_elements:
                    element.grid_forget()
                self.active_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
                self.active_elements[-1].grid(row = 0, column = 0)
                """
                button_text = '{:^10}'.format("\nSee final score\n")
                self.selection_confirmation_button.grid_forget()
                self.selection_confirmation_button = None
                self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                                    command=lambda : self.score()))
                self.sideboard_elements[-1].grid(row = 1, column = 0)
               
        elif len(self.selected_elements) > self.test_excercise_target_words_per_category:
            diff = self.test_excercise_target_words_per_category - len(self.selected_elements)
            self.notification_string.set("Deselect %i word(s)" %abs(diff))
            audio_string = "../assets/audio/too_many_words.mp3"
            self.enqueue_soundfiles(audio_string)
            self.UI["notification"] = Label(self.sideboard, bg = incorrect, textvariable = self.notification_string, font = self.app_font)
            self.UI["notification"].grid(row = 9, column = 0, columnspan = 3*width//4)
            
        elif len(self.selected_elements) < self.test_excercise_target_words_per_category:
            diff = self.test_excercise_target_words_per_category - len(self.selected_elements)
            audio_string = "../assets/audio/too_little_words.mp3"
            self.enqueue_soundfiles(audio_string)
            self.notification_string.set("Select %i more word(s)" %diff)
            self.UI["notification"] = Label(self.sideboard, bg = incorrect, textvariable = self.notification_string, font = self.app_font)
            self.UI["notification"].grid(row = 9, column = 0, columnspan = 3*width//4)

    def score(self):
        self.reset_grid()
        score = len(self.answers.keys())*self.test_excercise_target_words_per_category
        correct = 0
        count = 1
        correct_categories = 0
        attempted = 0
        self.sideboard.destroy()
        self.game_canvas.destroy()
        scoring_menu = VertAndHorizScrolledFrame(self.root, background)
        scoring_menu.pack()
        for key in self.answers.keys():
            local_correct = 0
            these_answers = []
            feedback = []
            for word in self.answers[key]:
                print(word[0].word)
                these_answers.append(word[0].word)
                attempted += 1
                if self.level == 1:
                    if word[0].has_same_phoneme_as(self.word_map[key]):
                        feedback.append("%s has the same vowel sound as %s"%(word[0], key))
                        local_correct += 1
                    else:
                        feedback.append("%s does not have the same vowel sound as %s"%(word[0], key))
                elif self.level == 2:
                    if word[0].has_same_spelling_pattern_as(self.word_map[key]):
                        feedback.append("%s has the same spelling pattern as %s"%(word[0], key))
                        local_correct += 1
                    else:
                        feedback.append("%s does not have the same spelling pattern as %s"%(word[0], key))
                elif self.level == 3:
                    if word[0].phoneme == self.word_map[key].phoneme and word[0].spelling_pattern == self.word_map[key].spelling_pattern:
                        feedback.append("%s has the same vowel sound and spelling pattern as %s"%(word[0], key))
                        local_correct += 1
                    elif word[0].phoneme != self.word_map[key].phoneme and word[0].spelling_pattern != self.word_map[key].spelling_pattern:
                        feedback.append("%s does not have the same vowel sound or spelling pattern as %s"%(word[0], key))
                    elif word[0].phoneme != self.word_map[key].phoneme and word[0].spelling_pattern == self.word_map[key].spelling_pattern:
                        feedback.append("%s does not have the same vowel sound as %s"%(word[0], key))
                    elif word[0].phoneme == self.word_map[key].phoneme and word[0].spelling_pattern != self.word_map[key].spelling_pattern:
                        feedback.append("%s does not have the same spelling pattern as %s"%(word[0], key))
            correct+= local_correct
            string = "Out of %i choices you found %i words that rhyme with %s" %(self.test_excercise_target_words_per_category, local_correct, key)
            self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = string, font = self.app_font))
            self.sideboard_elements[-1].grid(row = count, column = 0)
            count += 1
            answer_string = ", ".join(these_answers)
            string = "You selected: %s" %answer_string
            self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = string, font = self.app_font))
            self.sideboard_elements[-1].grid(row = count, column = 0)
            count += 1
            for item in feedback:
                self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = item, font = self.app_font))
                self.sideboard_elements[-1].grid(row = count, column = 0)
                count += 1

            if local_correct == self.test_excercise_target_words_per_category-1:
                correct_categories += 1
        string = "Overall, you scored %i/%i" %(correct, score)
        self.sideboard_elements.append(Label(scoring_menu.interior, bg = flipped_up, text = string, font = self.app_font))
        self.sideboard_elements[-1].grid(row = count+1, column = 0)
        count += 1
        button_text = '{:^10}'.format("\nBack to Main Menu\n")

        self.sideboard_elements.append(Button(scoring_menu.interior, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 0, column = 0)

        #init game_dat here
        
        if self.time_left == 0:
            self.game_dat["time"] = "0" 
            
        else:
            self.game_dat["time"] = self.time_left
        self.game_dat["complete"] = attempted
        self.game_dat["correct"] = correct
        self.game_dat["correct_categories"] = correct_categories
        self.game_dat["total_words"] = len(self.words_active)
        self.game_dat["total_categories"] = ",".join(self.target_patterns)
        self.game_dat["verbose_logs"] = feedback
        self.game_dat["passed"] = (correct_categories == len(self.answers.keys()))
        self.game_dat["score"] = correct/len(self.words_active)
        
    def flip_test(self, data):
        if q.empty() and not self.time_up():
            row = data[0]
            column = data[1]
            word = data[2]
            index = data[3]
            selected = data[4]
            button_text = '{:^25}'.format("\n%s\n" %word)
            if not selected:

                audio_string = "../assets/audio/matching/%s.mp3" %word
                self.enqueue_soundfiles(audio_string)

                self.selected_elements.append((word, index, row, column))

                self.active_elements[index].grid_forget()
                self.active_elements[index] = Button(self.game_canvas, bg = color_list[self.category_index], \
                                                text = button_text, font = self.app_font,\
                                                command=lambda data = [row, column, \
                                                self.words_active[index], index, not selected] : self.flip_test(data))
                self.active_elements[index].grid(row = row, column = column)

            else:
                delete_index = 0
                for i in range(len(self.selected_elements)):
                    print(self.selected_elements[i][0].word)
                    if self.selected_elements[i][0].word == word.word:
                        delete_index = i
                        break

                del self.selected_elements[delete_index]

                self.active_elements[index].grid_forget()
                self.active_elements[index] = Button(self.game_canvas, bg = flipped_up, \
                                                    text = button_text, font = self.app_font, command=lambda \
                                                    data = [row, column, self.words_active[index], index, \
                                                    not selected] : self.flip_test(data))
                self.active_elements[index].grid(row = row, column = column)
        elif self.time_up():
            
            self.submit()

    def create_board_teach_level1(self):
        self.reset_grid()
        self.complete = 0
        index = 0
        length = 4
        width = 6
        self.words_active = []
        """
        This would be determined randomly in the production version of the game
        """
        self.target_word_phoneme = "40"
        self.partner_phoneme = "49"
        self.partner_graphemes = ["iCe", "igh", "y"]
        self.vowel_types = ["Long i", "Short i"]

        target_word_count = 12
        partner_vowel_count = 4

        self.example_words = [self.partner_phoneme, self.target_word_phoneme]
        self.target_patterns = [self.partner_phoneme, self.target_word_phoneme]

        self.target_word_set = self.generate_word_set(target_word_count, self.target_word_phoneme)

        for vowel_sound in self.partner_graphemes:
            self.partner_word_set = self.generate_word_set(partner_vowel_count, vowel_sound)
            for index in self.partner_word_set:
                self.words_active.append(self.word_map[vowel_sound][index])

        for index in self.target_word_set:
            self.words_active.append(self.word_map[self.target_word_phoneme][index])

        self.words_active = self.shuffle(self.words_active)
        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()

        """
        menu_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = menu_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 14, column = 0, columnspan = width)
        """

        for i in range(len(self.vowel_types)):
            self.sideboard_columns[self.example_words[i]] = i
            self.sideboard_map[self.example_words[i]] = 2
            button_text = '{:^10}'.format("%s" %self.vowel_types[i])
            example_word = self.get_random_word_from_category(self.example_words[i])
            phone_file_name = self.vowel_types[i].replace(" ", "").lower()
            self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font, \
                                command=lambda \
                                data = "../assets/audio/%s.mp3,../assets/audio/x_says.mp3,../assets/audio/%ssound.mp3,../assets/audio/like_word_x.mp3,../assets/audio/matching/%s.mp3" %(phone_file_name, self.target_patterns[i], example_word) : self.play_again(data)))
            self.sideboard_elements[-1].grid(row = 0, column = i)
        index = 0
        for i in range(length):
            for j in range(width):
                self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = self.global_hidden, font = self.app_font,\
                    command=lambda data = [i, j, self.words_active[index], index, True] : self.flip_teach(data)))
                self.active_elements[-1].grid(row = i, column = j)

                index += 1
        audio_string = "../assets/audio/matching_teach_instructions_p1.mp3,../assets/audio/matching_teach_instructions_p2_level1.mp3"
        self.enqueue_soundfiles(audio_string)

    def create_board_teach_level2(self):
        self.reset_grid()
        self.complete = 0
        index = 0
        length = 4
        width = 6
        distractor_count = 6

        self.category_index = 0
        self.test_excercise_target_words_per_category = 6
        # type Word = list of all active words in the game
        self.words_active = []

        # self.active_incorrect = []
        # type Word - list of all actively selected words
        self.selected_elements = []

        # type Word - list of two sample words players find rhymes for
        self.goal_word_list = []

        self.word_set = set()

        self.goal_word_var = StringVar()
        self.button_text = StringVar()
        self.notification_string = StringVar()

        self.answers = defaultdict(list)
        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()

        # This would be determined randomly in the production version of the game
        self.active_sideboard_elements = defaultdict(list)
        self.categories = 4
        self.target_patterns = ["iCe", "igh", "y"]
        self.example_words = []
        target_word_count = 9

        for seq in self.target_patterns:
            self.sideboard_map[seq] = 6
            self.partner_word_set = self.generate_word_set(target_word_count, seq)
            for index in self.partner_word_set:
                self.words_active.append(self.word_map[seq][index])
            self.example_words.append(self.words_active[-1])
            del self.words_active[-1]

        self.words_active = self.shuffle(self.words_active)
        """
        menu_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = menu_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 14, column = 0, columnspan = width)
        """
        for i in range(len(self.target_patterns)):
            self.sideboard_columns[self.target_patterns[i]] = i
            self.sideboard_map[self.target_patterns[i]] = 2
            button_text = '{:^10}'.format("%s" %self.example_words[i])

            phone_file_name = self.target_patterns[i].replace(" ", "").lower()
            self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font, \
                                command=lambda data = ",".join(
                                                        [
                                                        "../assets/audio/matching/%s.mp3" %self.example_words[i],
                                                        "../assets/audio/spelling_cue.mp3",
                                                        "../assets/audio/%sspelling_pattern.mp3" %self.target_patterns[i],
                                                        ]
                                                        ) : self.play_again(data)))
            self.sideboard_elements[-1].grid(row = 0, column = i)
        index = 0

        for i in range(length):
            for j in range(width):
                self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = self.global_hidden, font = self.app_font,\
                    command=lambda data = [i, j, self.words_active[index], index, True] : self.flip_teach(data)))
                self.active_elements[-1].grid(row = i, column = j)

                index += 1
        audio_string = "../assets/audio/matching_teach_instructions_p1.mp3,../assets/audio/matching_teach_instructions_p2_level2.mp3"
        self.enqueue_soundfiles(audio_string)

    def create_board_teach_level3(self):
        self.reset_grid()
        self.complete = 0
        index = 0
        length = 4
        width = 6
        distractor_count = 6

        self.category_index = 0
        self.test_excercise_target_words_per_category = 6
        # type Word = list of all active words in the game
        self.words_active = []
        # type string - list of phoneme categories of active words

        # self.active_incorrect = []
        # type Word - list of all actively selected words
        self.selected_elements = []

        # type Word - list of two sample words players find rhymes for
        self.goal_word_list = []

        self.word_set = set()

        self.goal_word_var = StringVar()
        self.button_text = StringVar()
        self.notification_string = StringVar()

        self.answers = defaultdict(list)
        self.sideboard_map = defaultdict()
        self.sideboard_columns = defaultdict()

        # This would be determined randomly in the production version of the game
        self.active_sideboard_elements = defaultdict(list)
        self.categories = 4
        self.target_patterns = ["i", "iCe", "igh", "y"]
        self.example_words = []
        target_word_count = 7

        for seq in self.target_patterns:
            self.sideboard_map[seq] = 6
            self.partner_word_set = self.generate_word_set(target_word_count, seq)
            for index in self.partner_word_set:
                self.words_active.append(self.word_map[seq][index])
            self.example_words.append(self.words_active[-1])
            del self.words_active[-1]

        self.words_active = self.shuffle(self.words_active)

        """
        menu_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = menu_text, font = self.app_font,\
                                            command=lambda : self.main_menu()))
        self.sideboard_elements[-1].grid(row = 14, column = 0, columnspan = width)
        """
        for i in range(len(self.target_patterns)):
            self.sideboard_columns[self.target_patterns[i]] = i
            self.sideboard_map[self.target_patterns[i]] = 2
            button_text = '{:^10}'.format("%s" %self.example_words[i])

            phone_file_name = self.target_patterns[i].replace(" ", "").lower()
            self.sideboard_elements.append(Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font, \
                                command=lambda data = ",".join(
                                                        [
                                                        "../assets/audio/matching/%s.mp3" %self.example_words[i].word,\
                                                        "../assets/audio/x_says.mp3",\
                                                        "../assets/audio/%ssound.mp3" %self.example_words[i].phoneme,\
                                                        "../assets/audio/and.mp3",\
                                                        "../assets/audio/spelling_cue.mp3",\
                                                        "../assets/audio/%sspelling_pattern.mp3" %self.example_words[i].spelling_pattern\
                                                        ]
                                                        ) : self.play_again(data)))
            self.sideboard_elements[-1].grid(row = 0, column = i)
        index = 0

        for i in range(length):
            for j in range(width):
                self.active_elements.append(Button(self.game_canvas, bg = flipped_down, text = self.global_hidden, font = self.app_font,\
                    command=lambda data = [i, j, self.words_active[index], index, True] : self.flip_teach(data)))
                self.active_elements[-1].grid(row = i, column = j)

                index += 1
        audio_string = "../assets/audio/matching_teach_instructions_p1.mp3,../assets/audio/matching_teach_instructions_p2_level3.mp3"
        self.enqueue_soundfiles(audio_string)
        
    def flip_teach(self, data):
        if (q.empty() and mixer.music.get_busy()==0) and not self.time_up():
            row = data[0]
            column = data[1]
            word = data[2]
            index = data[3]
            is_face_down = data[4]

            if len(self.selected_elements) == 2:
                is_match, goal_word, feedback = self.check_match()
                if is_match:
                    self.clear_element(0)
                    self.clear_element(1)
                else:
                    self.switch_state(self.selected_elements[0][1], False,\
                        self.selected_elements[0][0], self.selected_elements[0][2], \
                        self.selected_elements[0][3])
                    self.switch_state(self.selected_elements[1][1], False,\
                        self.selected_elements[1][0], self.selected_elements[1][2], \
                        self.selected_elements[1][3])
                """
                if (word, index, row, column) in self.selected_elements:
                    self.selected_elements = []
                """
                self.selected_elements = []
                return


            if is_face_down:
                audio_string = "../assets/audio/matching/%s.mp3" %word
                thread = threading.Thread(target = self.enqueue_soundfiles, \
                                            args = (audio_string,))
                thread.start()
                self.switch_state(index, is_face_down, word, row, column)
                if len(self.selected_elements) == 1:
                    self.selected_elements.append((word, index, row, column))
                    goal_word = ""
                    is_match, goal_word, feedback = self.check_match()
                    if is_match: #two selected elements match
                        self.set_correct_or_incorrect(self.selected_elements[1][1], False,\
                            word, row, column, correct)
                        self.set_correct_or_incorrect(self.selected_elements[0][1], False,\
                            self.selected_elements[0][0], self.selected_elements[0][2], \
                            self.selected_elements[0][3], correct)

                        button_text = '{:^10}'.format("%s" %word)

                        audio_string = "../assets/audio/correct_tone1.mp3,../assets/audio/vowel_sound_does_match.mp3"
                        if self.level == 2:
                            audio_string = "../assets/audio/correct_tone1.mp3,../assets/audio/correct_spelling_pattern.mp3"
                        elif self.level == 3:
                            audio_string = "../assets/audio/correct_tone1.mp3,../assets/audio/correct_spelling_pattern_and_vowel_sound.mp3"

                        thread = threading.Thread(target = self.enqueue_soundfiles, \
                                                    args = (audio_string,))
                        thread.start()

                        self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
                        self.sideboard_elements[-1].grid(row = self.sideboard_map[goal_word], column = self.sideboard_columns[goal_word])
                        self.sideboard_map[goal_word] +=1
                        button_text = '{:^10}'.format("%s" %self.selected_elements[0][0])
                        self.sideboard_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
                        self.sideboard_elements[-1].grid(row = self.sideboard_map[goal_word], column = self.sideboard_columns[goal_word])
                        self.sideboard_map[goal_word] +=1

                        self.complete += 2
                        if self.complete == len(self.words_active):

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

                        audio_string = "../assets/audio/incorrect_tone1.mp3,../assets/audio/vowel_sound_doesnt_match.mp3"
                        if self.level == 2:
                            audio_string = "../assets/audio/incorrect_tone1.mp3,../assets/audio/incorrect_spelling_pattern.mp3"
                        elif self.level == 3:
                            # check if correct spelling pattern incorrect vowel sound
                            if self.selected_elements[0][0].spelling_pattern == self.selected_elements[1][0].spelling_pattern\
                                and self.selected_elements[0][0].phoneme != self.selected_elements[1][0].phoneme:
                                audio_string = "../assets/audio/incorrect_tone1.mp3,../assets/audio/correct_spelling_pattern.mp3,../assets/audio/and.mp3,../assets/audio/vowel_sound_doesnt_match.mp3"
                            elif self.selected_elements[0][0].spelling_pattern != self.selected_elements[1][0].spelling_pattern\
                                and self.selected_elements[0][0].phoneme == self.selected_elements[1][0].phoneme:# check if incorrect spelling pattern correct vowel sound
                                audio_string = "../assets/audio/incorrect_tone1.mp3,../assets/audio/incorrect_spelling_pattern_and_correct_vowel_sound.mp3"
                            elif self.selected_elements[0][0].spelling_pattern != self.selected_elements[1][0].spelling_pattern\
                                and self.selected_elements[0][0].phoneme != self.selected_elements[1][0].phoneme:# check if incorrect spelling pattern and correct vowel sound
                                audio_string = "../assets/audio/incorrect_tone1.mp3,../assets/audio/incorrect_spelling_pattern_and_vowel_sound.mp3"
                        thread = threading.Thread(target = self.enqueue_soundfiles, \
                                                    args = (audio_string,))
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
        elif self.time_up():
            print("You're done!")
            self.teach_breakdown()

    def teach_breakdown(self):
        button_text = '{:^10}'.format("\nYou ran out of time!\nDon't worry, you'll do better next time!\n")
        #timer_queue.put(None)
        if not self.time_up():
            time_minutes = self.time_left//60
            time_seconds = int(time_left) % 60
            button_text = '{:^10}'.format("Congratulations you finished with %i minutes and %i seconds left " %(time_minutes, time_seconds))
            self.game_dat["time"] = int(time_left)
        else:
            self.game_dat["time"] = 0
        
        self.game_dat["complete"] = self.complete
        self.game_dat["correct"] = 0
        self.game_dat["correct_categories"] = 0
        self.game_dat["total_words"] = len(self.words_active)
        self.game_dat["total_categories"] = ",".join(self.target_patterns)
        self.game_dat["verbose_logs"] = "NA"
        self.game_dat["passed"] = "NA"
        self.game_dat["score"] = 100.0

        self.reset_grid()
        self.game_canvas.destroy()
        
        #generate main menu button        
        self.active_elements.append(Label(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font))
        self.active_elements[-1].grid(row = 0, column = 0)
        button_text = '{:^10}'.format("\nBack to Main Menu\n")
        self.main_menu_button = Button(self.sideboard, bg = flipped_up, text = button_text, font = self.app_font,\
                                            command=self.main_menu)
        self.main_menu_button.grid(row = 1, column = 0)
        # self.root.destroy()

    """
    Generate list random distractor words that are currently not being tested
    Should not be all the same category(either by phoneme or grapheme)
    Parameters:
        number_to_generate - number of words to populate distractor list with
        unallowed_phonemes - list of phonemes that are currently being tested for
    """
    def load_distractor_words(self, number_to_generate, unallowed_phonemes):
        distractor_words = []

        while len(distractor_words) != number_to_generate:
            distractor_key = self.get_random_phoneme_or_grapheme(unallowed_phonemes)
            rand_index = int(RNG() * len(self.word_map[distractor_key]))
            print(len(self.word_map))
            if self.word_map[distractor_key][rand_index] in distractor_words:
                continue
            else:
                distractor_words.append(self.word_map[distractor_key][rand_index])
        return distractor_words

    def get_random_phoneme_or_grapheme(self, unallowed_phonemes):
        #shuffled_keys = self.shuffle(self.sequence_keys)
        ret_val = ""
        rand_index = int(RNG() * len(self.sequence_keys))
        while self.sequence_keys[rand_index] in unallowed_phonemes:
            rand_index = int(RNG() * len(self.sequence_keys))
        ret_val = self.sequence_keys[rand_index]
        return ret_val

    def set_correct_or_incorrect(self, index, is_face_down, word, row, column, color):
        self.active_elements[index].grid_forget()
        string_text = '{:^20}'.format("\n%s\n" %word.word)
        self.active_elements[index]=Button(self.game_canvas, bg = color, \
            text = string_text, font = self.app_font,\
            command=lambda data = [row, column, word, index, is_face_down] : self.flip_teach(data))
        self.active_elements[index].grid(row = row, column = column)

    def switch_state(self, index, is_face_down, word, row, column):
        if is_face_down:
            bg_color = flipped_up
            string_text = '{:^20}'.format("\n%s\n" %word.word)
            is_face_down = False
        else:
            bg_color = flipped_down
            string_text = self.global_hidden
            is_face_down = True

        self.active_elements[index].grid_forget()
        self.active_elements[index]=Button(self.game_canvas,bg = bg_color, text = string_text, font = self.app_font,\
            command=lambda data = [row, column, word, index, is_face_down] : self.flip_teach(data))
        self.active_elements[index].grid(row = row, column = column)

    def get_random_word_from_category(self, phoneme):
        #index into wordmap by phoneme
        for word in self.word_map[phoneme]:
            if word not in self.words_active:
                return word

    def generate_word_set(self, words_to_generate, category):
        return_set = set()
        while len(return_set) != words_to_generate:
            rand_index = int(RNG()*len(self.word_map[category]))
            return_set.add(rand_index)
        return return_set

    def play_again(self, data):
        if data == None:
            data = "../assets/audio/matching/%s.mp3" %self.example_words[self.category_index]
        if mixer.music.get_busy() == 0:
            self.enqueue_soundfiles(data)

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
        goal_word = ""
        if self.level == 1:
            if word1.has_same_phoneme_as(word2):
                for t_word in self.example_words:
                    if t_word == word1.phoneme:
                        goal_word = t_word
                        break
                return True, goal_word, "Correct info"
            else:
                return False, "", "incorrect"
        elif self.level == 2:
            if word1.has_same_spelling_pattern_as(word2):
                for t_word in self.example_words:
                    if t_word.has_same_spelling_pattern_as(word1):
                        goal_word = t_word
                        break
                return True, goal_word.spelling_pattern, "Correct info"
            else:
                return False, "", "incorrect"
        elif self.level == 3:
            if word1.has_same_spelling_pattern_as(word2) and word1.has_same_phoneme_as(word2):
                for t_word in self.example_words:
                    if t_word.has_same_spelling_pattern_as(word1) and t_word.has_same_phoneme_as(word1):
                        goal_word = t_word
                        break
                return True, goal_word.spelling_pattern, "Correct info"
            elif not word1.has_same_spelling_pattern_as(word2) and word1.has_same_phoneme_as(word2):
                return False, "", "incorrect"
            elif word1.has_same_spelling_pattern_as(word2) and not word1.has_same_phoneme_as(word2):
                return False, "", "incorrect"
            elif not word1.has_same_spelling_pattern_as(word2) and not word1.has_same_phoneme_as(word2):
                return False, "", "incorrect"


if __name__=='__main__':
    MatchingGame("Teach", 3)
