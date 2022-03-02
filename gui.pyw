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

    def changeText(self, tag, word, cols=None, saveTill=None, colType=None):
        if cols is None: cols = ['rgb(240, 240, 240)'] * len(word)
        if colType is None: colType = ['background-color'] * len(word)
        assert len(word) == len(cols)
        assert len(word) == len(colType)
        self.tags[tag] = self.tags[tag][0], word
        self.tags[tag] = self.tags[tag][0], word[:saveTill if saveTill is not None else len(word)]
        if (vac := self.lengthOfWord - len(word)) > 0:
            word += '_' * vac
            cols += ['rgb(240, 240, 240)'] * vac
            colType += ['background-color'] * vac
        elif vac < 0:
            word = word[:self.lengthOfWord]
            cols = cols[:self.lengthOfWord]
            colType = colType[:self.lengthOfWord]
        lab = self.tags[tag][0]
        colWords = ''.join(f'<span style="{t}:{c};font-size:20px;">&nbsp;{w}&nbsp;</span>'
                           for w, c, t in zip(word, cols, colType))
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

    def __setWords(self, lengthOfWord, numAttempts):
        self.wordz = Wordz(lengthOfWord, numAttempts)
        self.vbox.addWidget(self.wordz)

    def __setKeyBoard(self):
        self.keyBoard = KeyBoard(self.onKeyPress)
        self.vbox.addWidget(self.keyBoard)

    def __setIOInterface(self):
        guessFrame = Qt.QFrame()
        self.guessBut = Qt.QPushButton("Guess")
        self.guessBut.setFixedSize(100, 50)
        self.guessBut.clicked.connect(lambda: self.onGuessPress())
        self.guessLab = Qt.QLabel()

        hbox = Qt.QHBoxLayout()
        hbox.addWidget(self.guessBut)
        hbox.addWidget(self.guessLab)
        guessFrame.setLayout(hbox)
        self.vbox.addWidget(guessFrame)

        self.newGameBut = Qt.QPushButton("Play New Game")
        self.newGameBut.setFixedSize(150, 50)
        self.newGameBut.clicked.connect(lambda: self.__game_init())
        self.vbox.addWidget(self.newGameBut, alignment=Qt.Qt.AlignHCenter)

        self.guessDis()

    def guessDis(self, dis=True):
        if dis:
            self.keyBoard.setDisabled(True)
            self.guessBut.setDisabled(True)
            self.wordz.setDisabled(True)
        else:
            self.keyBoard.setDisabled(False)
            self.guessBut.setDisabled(False)
            self.wordz.setDisabled(False)

    # todo: make this common with cmd
    def guessLabInit(self): return f"Guess The {self.wordz.lengthOfWord} lettered word!"

    @staticmethod
    def guessLabWon(word, score):
        return f"Hurray! you guessed the correct word '{word}' " \
               f"with Score {score}/{cmd.numOfTrial}"

    @staticmethod
    def guessLabLost(word): return f"Oops! no more turns left! You Lost, The word was '{word}'"

    def __game_init(self):
        cmd.initialize()
        self.__word = cmd.genRandomWord()
        self.guessDis(False)
        for i in range(1, self.wordz.numAttempts + 1): self.wordz.changeText(i, '')
        self.keyBoard.colorIfy(*self.keyBoard.tags, col=self.keyBoard.BASE)
        self.guessLab.setText(self.guessLabInit())
        self.wordz.pos = 1

    def onGuessPress(self):
        guessedWord = self.wordz.tags[self.wordz.pos][1]
        if cmd.checkIfAllowed(guessedWord):
            self.guessLab.setText(self.guessLabInit())
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
                self.guessLab.setText(self.guessLabWon(guessedWord, self.wordz.numAttempts - self.wordz.pos + 2))
                self.guessDis()
            elif self.wordz.pos > self.wordz.numAttempts:
                self.guessLab.setText(self.guessLabLost(self.__word.upper()))
                self.guessDis()
            else:
                self.onKeyPress('')
        else: self.guessLab.setText(f"The Word '{guessedWord}' is not Valid")

    def onKeyPress(self, w):
        word = self.wordz.tags[self.wordz.pos][1] + w
        if w == '\b': word = word[:-2]
        if len(word) > self.wordz.lengthOfWord: word = word[:self.wordz.lengthOfWord]
        gWord = cmd.gWord.replace(' ', '')
        gWord = word + gWord[len(word):]
        cols = ['rgb(240, 240, 240)']*len(word) + \
               ['rgb(240, 240, 240)' if i == '_' else 'lightgreen' for i in gWord[len(word):]]
        self.wordz.changeText(self.wordz.pos, gWord, cols, saveTill=len(word))


def main():
    app = Qt.QApplication(sys.argv)
    win = Gui(cmd.lengthOfWords, cmd.numOfTrial)
    win.show()
    win.activateWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
