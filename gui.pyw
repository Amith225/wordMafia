import sys
import cmd
from PyQt5 import Qt


class KeyBoard(Qt.QWidget):
    KEYS = [c.upper() for c in "qwertyuiopasdfghjklzxcvbnm"]
    LAYERS = [10, 9, 7]

    BASE = "QPushButton{background-color: rgb(225, 225, 225);}" \
            "QPushButton::hover{background-color: lightblue;}"
    GREEN = "QPushButton{background-color: green;}" \
            "QPushButton::hover{background-color: lightgreen;}"
    YELLOW = "QPushButton{background-color: yellow;}" \
             "QPushButton::hover{background-color: lightyellow;}"
    GRAY = "QPushButton{background-color: gray;}" \
           "QPushButton::hover{background-color: rgb(175,175,175);}"

    def __init__(self, onButtonPress, *args, **kwargs):
        super(KeyBoard, self).__init__(*args, **kwargs)
        self.buttonHook = onButtonPress
        self.vbox = Qt.QVBoxLayout(self)
        self.setLayout(self.vbox)
        self.tags: dict[str, Qt.QPushButton] = {}
        self.draw()

    def draw(self):
        k = 0
        for j, l in enumerate(self.LAYERS):
            hbox = Qt.QHBoxLayout()
            hbox.addStretch(1)
            for i in range(l):
                button = Qt.QPushButton(self.KEYS[k+i])
                button.setFixedSize(50, 50)
                tag = self.KEYS[k + i]
                button.clicked.connect(lambda *_, t=tag: self.buttonHook(t))
                self.tags[tag] = button
                hbox.addWidget(button)
            k += l
            hbox.addStretch(1)
            self.vbox.addLayout(hbox)
        self.colorIfy(*self.tags, col=self.BASE)
        button = Qt.QPushButton("BackSpace")
        button.setStyleSheet(self.BASE)
        button.setFixedHeight(50)
        button.clicked.connect(lambda: self.buttonHook("\b"))
        self.vbox.addWidget(button)

    def colorIfy(self, *tags, col):
        for tag in tags:
            but = self.tags[tag]
            but.setStyleSheet(col)
            but.update()


class Wordz(Qt.QWidget):
    GREEN = "green"
    YELLOW = "yellow"
    GRAY = "gray"

    def __init__(self, lengthOfWord, numAttempts, *args, **kwargs):
        super(Wordz, self).__init__(*args, **kwargs)
        self.vbox = Qt.QVBoxLayout(self)
        self.vbox.setAlignment(Qt.Qt.AlignHCenter)
        self.setLayout(self.vbox)

        self.lengthOfWord = lengthOfWord
        self.numAttempts = numAttempts
        self.pos = 1
        self.tags: dict[int, (Qt.QLabel, str)] = {}
        self.draw()

    def draw(self):
        for i in range(self.numAttempts):
            i += 1
            lab = Qt.QLabel()
            lab.setFont(Qt.QFont("times"))
            self.tags[i] = lab, ''
            self.changeText(i, '')
            self.vbox.addWidget(lab)

    def changeText(self, tag, word, cols=None):
        if cols is None: cols = ['rgb(240, 240, 240)'] * len(word)
        assert len(word) == len(cols)
        self.tags[tag] = self.tags[tag][0], word
        if (vac := self.lengthOfWord - len(word)) > 0: word += '_' * vac; cols += ['rgb(240, 240, 240)'] * vac
        elif vac < 0: word = word[:self.lengthOfWord]; cols = cols[:self.lengthOfWord]
        lab = self.tags[tag][0]
        colWords = ''.join(f'<span style="background-color:{c};font-size:20px;">&nbsp;{w}&nbsp;</span>'
                           for w, c in zip(word, cols))
        lab.setText(f"{tag}.&nbsp;&nbsp;&nbsp;{colWords}")


class Gui(Qt.QWidget):
    WIN_TITLE = "Word Mafia"
    SIZE = (600, 400)

    def __init__(self, lengthOfWord, numOfTrial, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.WIN_TITLE)
        self.resize(*self.SIZE)

        self.vbox = Qt.QVBoxLayout(self)

        self.setLayout(self.vbox)
        self.__setWords(lengthOfWord, numOfTrial)
        self.__setKeyBoard()
        self.__setIOInterface()
        self.__game_init()

    def __setWords(self, lengthOfWord, numAttempts):
        self.wordz = Wordz(lengthOfWord, numAttempts)
        self.vbox.addWidget(self.wordz)

    def __setKeyBoard(self):
        self.keyBoard = KeyBoard(self.onKeyPress)
        self.vbox.addWidget(self.keyBoard)

    def __setIOInterface(self):
        guessFrame = Qt.QFrame()
        self.guessBut = Qt.QPushButton()
        self.guessBut.setFixedSize(100, 50)
        self.guessLab = Qt.QLabel(self.guessLabWord1())

        hbox = Qt.QHBoxLayout()
        hbox.addWidget(self.guessBut)
        hbox.addWidget(self.guessLab)
        guessFrame.setLayout(hbox)
        self.vbox.addWidget(guessFrame)

    def __toGuessBut(self):
        self.guessBut.setText("Guess")
        try: self.guessBut.clicked.disconnect()
        except TypeError: pass
        self.guessBut.clicked.connect(lambda: self.onGuessPress())
        self.keyBoard.setDisabled(False)

    def __toReGameBut(self):
        self.guessBut.setText("Play Again")
        try: self.guessBut.clicked.disconnect()
        except TypeError: pass
        self.guessBut.clicked.connect(lambda: self.__game_init())
        self.keyBoard.setDisabled(True)

    # todo: make this common with cmd
    def guessLabWord1(self): return f"Guess The {self.wordz.lengthOfWord} lettered toGuessWord!"

    @staticmethod
    def guessLabWon(word): return f"Hurray you guessed the correct toGuessWord '{word}'"

    @staticmethod
    def guessLabLost(word): return f"Oops no more turns left! You Lost, The toGuessWord was '{word}'"

    def __game_init(self):
        cmd.initialize()
        self.__word = cmd.genRandomWord()
        self.__toGuessBut()
        for i in range(1, self.wordz.numAttempts + 1): self.wordz.changeText(i, '')
        self.keyBoard.colorIfy(*self.keyBoard.tags, col=self.keyBoard.BASE)
        self.wordz.pos = 1

    def onGuessPress(self):
        guessedWord = self.wordz.tags[self.wordz.pos][1]
        if cmd.checkIfAllowed(guessedWord):
            self.guessLab.setText(self.guessLabWord1())
            greenWords, yellowWords, grayWords = cmd.checkTheWords(self.__word, guessedWord)
            self.keyBoard.colorIfy(*[guessedWord[i].upper() for i in grayWords], col=self.keyBoard.GRAY)
            self.keyBoard.colorIfy(*[guessedWord[i].upper() for i in yellowWords], col=self.keyBoard.YELLOW)
            self.keyBoard.colorIfy(*[guessedWord[i].upper() for i in greenWords], col=self.keyBoard.GREEN)
            cmd.updateGwordAndHword(guessedWord, greenWords, yellowWords)
            g, y, gr = self.wordz.GREEN, self.wordz.YELLOW, self.wordz.GRAY
            self.wordz.changeText(self.wordz.pos, guessedWord, [g if i in greenWords else (y if i in yellowWords
                                                                                           else gr)
                                                                for i, w in enumerate(guessedWord)])
            self.wordz.pos += 1
            if guessedWord.lower() == self.__word.lower():
                self.guessLab.setText(self.guessLabWon(guessedWord))
                self.__toReGameBut()
            elif self.wordz.pos > self.wordz.numAttempts:
                self.guessLab.setText(self.guessLabLost(self.__word.upper()))
                self.__toReGameBut()
        else: self.guessLab.setText(f"The Word '{guessedWord}' is not Valid")

    def onKeyPress(self, w):
        word = self.wordz.tags[self.wordz.pos][1] + w
        if w == '\b': word = word[:-2]
        if len(word) > self.wordz.lengthOfWord: word = word[:self.wordz.lengthOfWord]
        self.wordz.changeText(self.wordz.pos, word)


def main():
    app = Qt.QApplication(sys.argv)
    win = Gui(cmd.lengthOfWords, cmd.numOfTrial)
    win.show()
    win.activateWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
