import random
import os

from .colVars import ColVars as Col

lengthOfWords = 5
numOfTrial = 6
with open("./assets/allowed.txt", 'r') as file: allowedWords = file.read().splitlines()
with open("./assets/sample.txt", 'r') as file: guessableWords = file.read().splitlines()
KEYS, LAYERS = [c.upper() for c in "qwertyuiopasdfghjklzxcvbnm"], [10, 9, 7]
trialTillNow: int; KEYS_COL: list[Col.C]; gWord: str; wordHistory: list[str]; prevNotAllowed: bool; prevWord: str


def initialize():
    global trialTillNow, KEYS_COL, gWord, wordHistory, prevNotAllowed, prevWord
    trialTillNow, KEYS_COL, gWord, wordHistory = 0, [Col.CWHITEBG] * len(KEYS), " _ " * lengthOfWords, []
    prevNotAllowed, prevWord = False, ''


def checkIfAllowed(guessedWord):
    guessedWord = guessedWord.lower()
    if guessedWord in allowedWords or guessedWord in guessableWords: return True
    else: return False


def checkTheWords(toGuessWord, guessedWord):
    guessedWord, toGuessWord = guessedWord.lower(), toGuessWord.lower()
    correctPosList, letterInWordList, letterAlreadyThere, wrongLetterList = [], [], [], []
    for i in range(len(toGuessWord)):
        l1, l2 = guessedWord[i], toGuessWord[i]
        if l1 == l2:
            correctPosList.append(i)
        elif toGuessWord.count(l1) - gWord.count(l1.upper()) > 0 and l1 in toGuessWord and \
                toGuessWord.count(l1) - letterAlreadyThere.count(l1) > 0:
            letterInWordList.append(i)
            letterAlreadyThere.append(l1)
        elif not gWord.count(l1.upper()): wrongLetterList.append(i)

    return correctPosList, letterInWordList, wrongLetterList


def updateGwordAndHword(guessedWord, greenWords, yellowWords):
    global gWord
    hWord = ''
    for i, c in enumerate(guessedWord):
        if i in greenWords:
            gWord = gWord[:i * 3 + 1] + c.upper() + gWord[i * 3 + 1 + 1:]
            hWord += Col.CGREENBG
        elif i in yellowWords:
            hWord += Col.CYELLOWBG
        else:
            hWord += Col.CGREYBG
        hWord += Col.CBLACK + ' ' + c.upper() + ' ' + Col.CEND
    wordHistory.append(hWord)


def genRandomWord(): return random.choice(guessableWords)


def keyBoard():
    i = prevLayer = 0
    for layer in LAYERS:
        numSpace = prevLayer - layer
        print(' ' * (numSpace if numSpace > 0 else 0), end='')
        for keyCol, key in zip(KEYS_COL[i:i+layer], KEYS[i:i+layer]):
            print(f"{keyCol}{Col.CBLACK} {key} {Col.CEND}", end='')
        print()
        prevLayer = layer
        i += layer
    print()


def interface():
    global prevWord, prevNotAllowed
    os.system('cls')
    keyBoard()
    [print(w) for i, w in enumerate(wordHistory)]
    print(gWord)
    if prevNotAllowed: print(f"The Word '{prevWord}' is not allowed")
    inp = input(
        f"Give a {lengthOfWords} lettered Word(you have {numOfTrial - trialTillNow + 1}/{numOfTrial} trials left): ")
    prevWord = inp

    if checkIfAllowed(inp):
        prevNotAllowed = False
        return inp
    else:
        prevNotAllowed = True
        return interface()


def game():
    initialize()
    word = genRandomWord()
    winFlag = False
    global trialTillNow, gWord
    while trialTillNow < numOfTrial:
        trialTillNow += 1
        guessedWord = interface()
        greenWords, yellowWords, grayWords = checkTheWords(word, guessedWord)
        for grayWord in grayWords: KEYS_COL[KEYS.index(guessedWord[grayWord].upper())] = Col.CGREYBG
        for yellowWord in yellowWords: KEYS_COL[KEYS.index(guessedWord[yellowWord].upper())] = Col.CYELLOWBG
        for greenWord in greenWords: KEYS_COL[KEYS.index(guessedWord[greenWord].upper())] = Col.CGREENBG
        updateGwordAndHword(guessedWord, greenWords, yellowWords)
        if guessedWord == word:
            winFlag = True
            break
    if winFlag: print(f"Hurray! You Won with {numOfTrial - trialTillNow + 2}/{numOfTrial}")
    else: print("U ran out tries")
    print(f"The Correct Word Was '{word}'", end='\n\n')


def main():
    while 1:
        inp = input("Do You Want To PLay 'Word Mafia' (y or n): ")
        if inp.lower() == 'y': game()
        else: break
