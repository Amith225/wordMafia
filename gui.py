import sys
import cmd
from PyQt5 import Qt


class KeyBoard(Qt.QWidget):
    KEYS = [c.upper() for c in "qwertyuiopasdfghjklzxcvbnm"]
    LAYERS = [10, 9, 7]

    GREEN = "QPushButton{background-color: green;}" \
            "QPushButton::hover{background-color: lightgreen;}"
    RED = "QPushButton{background-color: red;}" \
          "QPushButton::hover{background-color: rgb(255,127,127);}"
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
        button = Qt.QPushButton("BackSpace")
        button.clicked.connect(lambda: self.buttonHook("\b"))
        self.vbox.addWidget(button)

    def colorIfy(self, *tags, col):
        for tag in tags:
            but = self.tags[tag]
            but.setStyleSheet(col)
            but.update()


class Wordz(Qt.QWidget):
    GREEN = "green"
    RED = "red"
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
            lab = Qt.QLabel(f"{i}.   {'_ '*self.lengthOfWord}")
            lab.setFont(Qt.QFont("times", 11))
            self.tags[i] = lab, ''
            self.vbox.addWidget(lab)

    def changeText(self, tag, word, cols=None):
        if cols is None: cols = ['black'] * len(word)
        assert len(word) == len(cols)
        self.tags[tag] = self.tags[tag][0], word
        if (vac := self.lengthOfWord - len(word)) > 0: word += '_'*vac; cols += ['black']*vac
        elif vac < 0: word = word[:self.lengthOfWord]; cols = cols[:self.lengthOfWord]
        lab = self.tags[tag][0]
        lab.setText(f"{tag}.&nbsp;&nbsp;&nbsp;{' '.join(f'<font color={c}>{w}</font>' for w, c in zip(word, cols))}")


class Gui(Qt.QWidget):
    WIN_TITLE = "Word Mafia"
    SIZE = (600, 400)

    def __init__(self, lengthOfWord, numAttempts, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.WIN_TITLE)
        self.resize(*self.SIZE)

        self.vbox = Qt.QVBoxLayout(self)

        self.setLayout(self.vbox)
        self.__setWords(lengthOfWord, numAttempts)
        self.__setKeyBoard()
        self.__setIOInterface()

    def __setWords(self, lengthOfWord, numAttempts):
        self.wordz = Wordz(lengthOfWord, numAttempts, self)
        self.vbox.addWidget(self.wordz)

    def __setKeyBoard(self):
        self.keyBoard = KeyBoard(self.onKeyPress, self)
        self.vbox.addWidget(self.keyBoard)

    def __setIOInterface(self):
        guessBut = Qt.QPushButton("Guess")
        guessBut.setFixedSize(100, 50)
        guessBut.clicked.connect(lambda: self.onGuessPress())
        self.vbox.addWidget(guessBut)

    def onGuessPress(self):
        print(self.wordz.tags[self.wordz.pos][1])

    def onKeyPress(self, w):
        word = self.wordz.tags[self.wordz.pos][1]
        self.wordz.changeText(self.wordz.pos, word + w if w != '\b' else word[:-1])


def main():
    app = Qt.QApplication(sys.argv)
    lengthOfWord, numOfTrial = cmd.lengthOfWords, cmd.numOfTrial
    win = Gui(lengthOfWord, numOfTrial)
    win.show()
    sys.exit(app.exec_())
