from PyQt5 import uic, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from random import shuffle
from pygame import mixer
import sys
import json
import webbrowser
import requests
import html

mixer.init()

quiz_category = None
quiz_ended = False
quiz_length = 0
trivia_quiz = None
custom_path = None
sound_volume = 1
score = 0

mixer.music.load("SFX/menu_music.ogg")
mixer.music.play(-1)

class Home(QMainWindow):
    def __init__(self):
        super(Home, self).__init__()
        uic.loadUi("UI/home.ui", self)
        self.setWindowTitle("Home - Counting Brain Cells")
        self.menu_bar()
        self.category_buttons()
        self.show()
    
    def menu_bar(self):
        self.actionAbout.triggered.connect(self.about)
        self.actionWebsite.triggered.connect(self.website)
        self.actionQuit.triggered.connect(self.quit)
        self.actionGithub.triggered.connect(self.view_github)
        self.actionCredits.triggered.connect(self.view_credits)
        self.actionSound.triggered.connect(self.audioSettings)

    def category_buttons(self):
        self.category1.setStyleSheet("background-image : url(images/buttons/tech.jpg);")
        self.category2.setStyleSheet("background-image : url(images/buttons/maths.jpg);")
        self.category3.setStyleSheet("background-image : url(images/buttons/riddles.jpg);")
        self.category4.setStyleSheet("background-image : url(images/buttons/gaming.jpg);")
        self.category5.setStyleSheet("background-image : url(images/buttons/trivia_db.jpg);")
        self.category6.setStyleSheet("background-image : url(images/buttons/custom.jpg);")


        self.category1.clicked.connect(lambda:self.quiz("Tech"))
        self.category2.clicked.connect(lambda:self.quiz("Maths"))
        self.category3.clicked.connect(lambda:self.quiz("Riddles"))
        self.category4.clicked.connect(lambda:self.quiz("Gaming"))
        self.category5.clicked.connect(self.trivia_config)
        self.category6.clicked.connect(self.load_quiz)

    def load_quiz(self):
        load_dialog = loadCustom()
        load_dialog.exec()

    def quiz(self,category):
        global quiz_category

        quiz_category = category
        question_page = questionPage()
        widget.addWidget(question_page)
        widget.setCurrentIndex(3)
        question_page.run_quiz()

    def trivia_config(self):
        config = triviaConfigure()
        config.exec()
    
    def audioSettings(self):
        settings = soundSettings()
        settings.exec()

    def about(self):
        about = aboutDialog()
        about.exec()
    def view_credits(self):
        credits = creditsDialog()
        credits.exec()
    def website(self):
        webbrowser.open("https://dragonrider8128.github.io/counting-brain-cells")
    def view_github(self):
        webbrowser.open("https://github.com/DragonRider8128/CountingBrainCells")
    def quit(self):
        QApplication.quit()

class soundSettings(QDialog):
    def __init__(self):
        global sound_volume

        super(soundSettings, self).__init__()
        uic.loadUi("UI/audioDialog.ui", self)
        
        self.mute = QPixmap("Images/mute.png")
        self.volume_img = QPixmap("Images/volume.png")
        self.cancel.rejected.connect(self.close)
        self.music_slider.setValue(mixer.music.get_volume()*100)
        self.sfx_slider.setValue(sound_volume*100)
        self.music_slider.valueChanged.connect(self.music_volume)
        self.sfx_slider.valueChanged.connect(self.sfx_volume)

        if self.music_slider.value() == 0:
            self.icon.setPixmap(self.mute)
        else:
            self.icon.setPixmap(self.volume_img)
        
        if self.sfx_slider.value() == 0:
            self.icon_sfx.setPixmap(self.mute)
        else:
            self.icon_sfx.setPixmap(self.volume_img)
    
    def music_volume(self):
        volume = float(self.music_slider.value()/100)
        mixer.music.set_volume(volume)

        if self.music_slider.value() == 0:
            self.icon.setPixmap(self.mute)
        else:
            self.icon.setPixmap(self.volume_img)
    
    def sfx_volume(self):
        global sound_volume

        sound_volume = float(self.sfx_slider.value()/100)

        sfx_check = mixer.Sound("SFX/sfx_check.ogg")
        sfx_check.set_volume(sound_volume)
        sfx_check.play()

        if self.sfx_slider.value() == 0:
            self.icon_sfx.setPixmap(self.mute)
        else:
            self.icon_sfx.setPixmap(self.volume_img)
 

class questionPage(QMainWindow):
    def __init__(self):
        global score
        global quiz_ended

        mixer.music.stop()
        mixer.music.load("SFX/quiz_music.wav")
        mixer.music.play(-1)

        super(questionPage, self).__init__()
        uic.loadUi("UI/question.ui", self)
        widget.setWindowTitle("Counting Brain Cells - " + quiz_category)
        self.home.clicked.connect(self.go_home)
        self.next_question.clicked.connect(self.next_pressed)
        self.option1.toggled.connect(self.radio_option)
        self.option2.toggled.connect(self.radio_option)
        self.option3.toggled.connect(self.radio_option)
        self.option4.toggled.connect(self.radio_option)
        self.current_question = 0
        self.input = ""
        self.show()

        score = 0

    def radio_option(self):
        radioBtn = self.sender()

        if radioBtn.isChecked():
            self.input = radioBtn.text()
        else:
            radioBtn.setChecked(False)


    def go_home(self):
        widget.removeWidget(self)
        widget.setCurrentIndex(0)
        widget.setWindowTitle("Counting Brain Cells")
  

        mixer.music.stop()
        mixer.music.load("SFX/menu_music.ogg")
        mixer.music.play()

    def next_pressed(self):
        global score
        global result
        global quiz_ended
        global end_screen
        global quiz_category


        if quiz_category != "Trivia":
            answers = self.quiz[self.current_question]["correct_answer"]
            self.input = self.user_input.text()

            for i in range(len(answers)):
                answers[i] = answers[i].upper()
        else:
            answers = [self.quiz[self.current_question]["correct_answer"].upper()]
            

        if self.input.upper() in answers:
            score += 1
            self.score_label.setText("Score: " + str(score))

            result.wrong.hide()
            result.correct.show()
            result.result.setText("Correct")
            result.correct_answer.setText("Correct Answer: " + answers[0])
            widget.setCurrentIndex(1)
        else:
            result.correct.hide()
            result.wrong.show()
            result.result.setText("Incorrect")
            result.correct_answer.setText("Correct Answer: " + answers[0])
            widget.setCurrentIndex(1)

        self.user_input.clear()
        self.current_question += 1
        self.question_num.setText("Question: " + str(self.current_question + 1)+"/"+str(quiz_length))

        if self.current_question > len(self.quiz)-1:
            widget.removeWidget(self)
            quiz_ended = True
        else:
            if quiz_category == "Trivia":              
                self.multi_options = [self.quiz[self.current_question]["correct_answer"]]

                for option in self.quiz[self.current_question]["incorrect_answers"]:
                    self.multi_options.append(option)
            
                shuffle(self.multi_options)

                self.option1.setText(self.multi_options[0])
                self.option2.setText(self.multi_options[1])
            
                if self.quiz[self.current_question]["type"] != "boolean":
                    self.option3.setText(self.multi_options[2])
                    self.option4.setText(self.multi_options[3])
                    self.option3.show()
                    self.option4.show()
                else:
                    self.option3.hide()
                    self.option4.hide()
                
                self.radioGroup.setExclusive(False)
                self.option1.setChecked(False)
                self.option2.setChecked(False)
                self.option3.setChecked(False)
                self.option4.setChecked(False)
                self.radioGroup.setExclusive(True)
            
            self.question_label.setText(self.quiz[self.current_question]["question"])


    def run_quiz(self):
        global quiz_length
        global quiz_category
        global trivia_quiz
        global custom_path

        quiz_paths = {"Tech":"JSON/tech.json", "Maths":"JSON/maths.json", "Riddles":"JSON/riddles.json","Gaming":"JSON/gaming.json","Custom":custom_path}

        if quiz_category == "Trivia":
            self.quiz = trivia_quiz
            shuffle(self.quiz)
        elif quiz_category == "Custom":
            try:
                with open(custom_path,"r") as f:
                    custom_test = json.load(f)
                    f.close()
                
                for question in custom_test:
                    test_question  = question["question"]
                    test_answer = question["correct_answer"]

                    if not isinstance(test_answer,list) and isinstance(test_question, str):
                        raise ValueError("Invalid JSON.")
            except:
                self.go_home()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Invalid File")
                msg.setInformativeText("Make sure you formatting is valid and it follows the template.")
                msg.setWindowTitle("Custom File Error")
                msg.exec_()
                return

        if quiz_category != "Trivia":
            with open(quiz_paths[quiz_category],"r") as f:
                self.quiz = json.load(f)
                f.close()
            shuffle(self.quiz)
            self.user_input.show()
            self.option1.hide()
            self.option2.hide()
            self.option3.hide()
            self.option4.hide()

        else:
            self.user_input.hide()
            self.option1.show()
            self.option2.show()
            self.option3.show()
            self.option4.show()

            self.radioGroup = QButtonGroup()
            self.radioGroup.setExclusive(True)
            self.radioGroup.addButton(self.option1)
            self.radioGroup.addButton(self.option2)
            self.radioGroup.addButton(self.option3)
            self.radioGroup.addButton(self.option4)
            

            self.multi_options = [self.quiz[self.current_question]["correct_answer"]]

            for option in self.quiz[self.current_question]["incorrect_answers"]:
                self.multi_options.append(option)
            
            shuffle(self.multi_options)

            self.option1.setText(self.multi_options[0])
            self.option2.setText(self.multi_options[1])
            
            if self.quiz[self.current_question]["type"] != "boolean":
                self.option3.setText(self.multi_options[2])
                self.option4.setText(self.multi_options[3])
            else:
                self.option3.hide()
                self.option4.hide()
            
        quiz_length = len(self.quiz)
        self.question_label.setText(self.quiz[self.current_question]["question"])
        self.question_num.setText("Question: " + str(self.current_question + 1)+"/"+str(quiz_length))
        self.score_label.setText("Score: 0")

class loadCustom(QDialog):
    def __init__(self):
        super(loadCustom, self).__init__()
        uic.loadUi("UI/load_quiz.ui",self)
        self.load_btn.clicked.connect(self.load_file)
    
    def load_file(self):
        global quiz_category
        global custom_path

        fname = QFileDialog.getOpenFileName(self, "Load Quiz File", "", "JSON Files (*json)")[0]
        
        if fname and fname != "":
            custom_path = fname
            self.close()
            quiz_category = "Custom"
            question_page = questionPage()
            widget.addWidget(question_page)
            widget.setCurrentIndex(3)
            question_page.run_quiz()
        

class Result(QMainWindow):
    def __init__(self):
        super(Result, self).__init__()
        uic.loadUi("UI/result.ui", self)
        self.go_btn.clicked.connect(self.go)
    
    def go(self):
        global quiz_ended
        if quiz_ended:
            widget.setCurrentIndex(2)
            widget.setWindowTitle("Counting Brain Cells")
            end_screen.show_result()
            quiz_ended = False
        else:
            widget.setCurrentIndex(3)

class endScreen(QMainWindow):
    def __init__(self):
        super(endScreen, self).__init__()
        uic.loadUi("UI/end_screen.ui", self)
        self.home_btn.clicked.connect(self.home)
    
    def home(self):
        widget.setCurrentIndex(0)
        mixer.pause()
        mixer.music.stop()
        mixer.music.load("SFX/menu_music.ogg")
        mixer.music.play()
        
    def show_result(self):
        global score
        global quiz_length
        global sound_volume

        mixer.music.stop()
        fail = mixer.Sound("SFX/fail.ogg")
        illuminati = mixer.Sound("SFX/illuminati.ogg")
        win = mixer.Sound("SFX/win.wav")
        party = mixer.Sound("SFX/epic.ogg")

        fail.set_volume(sound_volume)
        illuminati.set_volume(sound_volume)
        win.set_volume(sound_volume)
        party.set_volume(sound_volume)

        brains = [self.zero,self.one,self.three,self.four,self.full]

        for brain in brains:
            brain.hide()
        
        self.score_label.setText("Score: " + str(score))

        if score <= quiz_length/10*3:
            self.zero.show()
            self.title.setText(' "You are so dumb, it is a surprise you were able to do this quiz in the first place." ')
            self.amount.setText("1 Brain Cell")
            fail.play()
        elif score > quiz_length/10*3 and score < quiz_length/2:
            self.one.show()
            self.title.setText(' "You think you are really smart but in reality you have an IQ of an amoeba. But I will be kind and give you a normal brain" ')
            self.amount.setText("55.5 Brain Cells")
            win.play()
        elif score >= quiz_length/2 and score < quiz_length/4*3:
            self.three.show()
            self.title.setText(' "You are above average in your intelligence. This may sound great, but in reality, the majority are dumbos anyway." ')
            self.amount.setText("100 Brain Cells")
            win.play()

        elif score >= quiz_length/4*3 and score < quiz_length:
            self.four.show()
            self.title.setText(' "Wow! I am surprised you even got that far to get this result. You have high intelligence (not really but what evs)." ')
            self.amount.setText("8128 Million Brain Cells")
            party.play()
        elif score == quiz_length:
            self.full.show()
            self.title.setText(' "You have the highest intelligence possible (that is if you don\'t count me). You are, logically, in the illuminati as you are using your sources to cheat, so I can\'t speak further." ')
            self.amount.setText("∞ Brain Cells")
            illuminati.play()

        self.title.setStyleSheet("color: #ff0516")
        self.amount.setStyleSheet("color: #8b80aa")


class triviaConfigure(QDialog):
    def __init__(self):
        super(triviaConfigure, self).__init__()
        uic.loadUi("UI/choose_menu.ui", self)
        self.play_btn.clicked.connect(self.play)
    
    def play(self):
        global quiz_category
        global trivia_quiz

        question_amount = self.question_amount.value()

        if self.difficulty.currentText() == "Any Difficulty":
            difficulty = ""
        else:
            difficulty = self.difficulty.currentText().lower()

        if self.category.currentText() == "Any Category":
            category=""
        else:
            category = str(self.category.currentIndex() + 8)

            count_url = "https://opentdb.com/api_count.php?category="+str(category)
            response = requests.get(count_url)
            count = response.json()["category_question_count"]

            if difficulty == "":
                if count["total_question_count"] < question_amount:
                    question_amount = count["total_question_count"]
                    self.information()

            else:
                if count["total_"+difficulty+"_question_count"] < question_amount:
                    question_amount = count["total_"+difficulty+"_question_count"]
                    self.information()


        url = "https://opentdb.com/api.php?amount="+str(question_amount)+"&category="+category+"&difficulty="+difficulty+""
        
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Can't connect to database.")
            msg.setInformativeText("Check your internet connection.")
            msg.setWindowTitle("Connection Error")
            msg.exec_()
            self.close()
            return

        trivia_quiz = response.json()["results"]
        
        for question in trivia_quiz:
            question["question"] = html.unescape(question["question"])
            question["correct_answer"] = html.unescape(question["correct_answer"])
            
            for i in range(len(question["incorrect_answers"])):
                question["incorrect_answers"][i] = html.unescape(question["incorrect_answers"][i])

        self.close()
        quiz_category = "Trivia"
        question_page = questionPage()
        widget.addWidget(question_page)
        widget.setCurrentIndex(3)
        question_page.run_quiz()
    
    def information(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Enough Questions Not Available.")
        msg.setInformativeText("Giving you maximum available.")
        msg.setWindowTitle("Configuration Issue")
        msg.exec_()

class aboutDialog(QDialog):
    def __init__(self):
        super(aboutDialog, self).__init__()
        uic.loadUi("UI/aboutDialog.ui", self)
        self.buttonBox.rejected.connect(self.close)

class creditsDialog(QDialog):
    def __init__(self):
        super(creditsDialog, self).__init__()
        uic.loadUi("UI/credits.ui", self)

app = QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon('Images/icon.png'))

widget = QStackedWidget()
home = Home()
result = Result()
end_screen = endScreen()

widget.addWidget(home)
widget.addWidget(result)
widget.addWidget(end_screen)

widget.setWindowTitle("Counting Brain Cells")
widget.setFixedWidth(1124)
widget.setFixedHeight(664)
widget.show()

app.exec_()