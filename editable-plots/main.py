from plotOpeningScreen import *
import PIL

if __name__ == "__main__":
    print("Using kiwisolver version", kiwisolver.__version__)
    print("Using Pillow version", PIL.__version__)
    menu = MenuScreen()
    menu.View()