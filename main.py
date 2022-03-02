from src import gui
from src import cmd


def main():
    inp = input('Gui:g or Cmd:c > ').lower()
    if inp == 'g':
        gui.main()
    elif inp == 'c':
        cmd.main()


if __name__ == '__main__':
    main()
