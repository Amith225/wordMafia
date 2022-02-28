import random
import os
from colVars import PrintVars as Pv

lengthOfWords = 5
numOfTrial = 6
with open("allowed.txt", 'r') as file:
    allowedList = file.read().splitlines()
with open("sample.txt", 'r') as file:
    sampleList = file.read().splitlines()
KEYS = [c.upper() for c in "qwertyuiopasdfghjklzxcvbnm"]
LAYERS = [10, 9, 7]
trailTillNow, KEYS_COL, gWord = 0, [Pv.CWHITEBG] * len(KEYS), "_"*lengthOfWords


def initialize():
    global trailTillNow, KEYS_COL, gWord
    trailTillNow = 0
    KEYS_COL = [Pv.CWHITEBG] * len(KEYS)
    gWord = "_"*lengthOfWords


def checkIfAllowed(inp):
    if inp in allowedList or inp in sampleList:
        return True
    else:
        return False


def checkRules(word, inp):
    rightPosList = []
    correctWordList = []
    wrongWordList = []
    for l1, l2 in zip(inp, word):
        if l1 == l2:
            rightPosList.append(l1)
        elif l1 in word:
            if l1 not in correctWordList:
                correctWordList.append(l1)
        else:
            wrongWordList.append(l1)

    return rightPosList, correctWordList, wrongWordList


def genRandomWord():
    return random.choice(sampleList)


def keyBoard():
    i = 0
    prevLayer = 0
    for layer in LAYERS:
        numSpace = prevLayer - layer
        print(' '*(numSpace if numSpace > 0 else 0), end='')
        for key_col, key in zip(KEYS_COL[i:i+layer], KEYS[i:i+layer]):
            print(key_col + Pv.CBLACK + ' ' + key + ' ' + Pv.CEND, end='')
        print()
        prevLayer = layer
        i += layer


prevNotAllowed, prevWord = False, ''


def interface():
    global prevWord, prevNotAllowed
    os.system('cls')
    keyBoard()
    print(' '.join(gWord))
    if prevNotAllowed:
        print(f"word '{prevWord}' not allowed")
    inp = input(f"Give a {lengthOfWords} lettered word(you have {numOfTrial - trailTillNow + 1} trails left): ")
    prevWord = inp
    allowedFlag = checkIfAllowed(inp)

    if allowedFlag:
        prevNotAllowed = False
        return inp
    else:
        prevNotAllowed = True
        return interface()


def game():
    initialize()
    word = genRandomWord()
    winFlag = False
    global trailTillNow, gWord
    while trailTillNow < 6:
        trailTillNow += 1
        inp = interface()
        greenWords, yellowWords, grayWords = checkRules(word, inp)
        for grayWord in grayWords:
            i = KEYS.index(grayWord.upper())
            KEYS_COL[i] = Pv.CGREYBG
        for yellowWord in yellowWords:
            i = KEYS.index(yellowWord.upper())
            if KEYS_COL[i] == Pv.CWHITEBG:
                KEYS_COL[i] = Pv.CYELLOWBG
        for greenWord in greenWords:
            i = KEYS.index(greenWord.upper())
            KEYS_COL[i] = Pv.CGREENBG
        for i, c in enumerate(inp):
            if c in greenWords:
                gWord = gWord[:i] + c.upper() + gWord[i+1:]
        if inp == word:
            winFlag = True
            break
    if winFlag:
        print("You Won")
    else:
        print("U ran out tries")
    print(f"The Correct Word Was '{word}'")
    print()


if __name__ == '__main__':
    while 1:
        inp = input("Do You Want To PLay 'Word Mafia' (y or n): ")
        if inp.lower() == 'y':
            game()
        else:
            break
