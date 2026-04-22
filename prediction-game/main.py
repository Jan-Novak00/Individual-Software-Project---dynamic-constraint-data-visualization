import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from pathlib import Path
from predictiongame import GameFactory, GameUI, LoadFailedException

BASE_DIR = Path(__file__).resolve().parent

def StartGame():
    root = tk.Tk()
    root.title("Prediction game")
    root.geometry("220x100")

    def openGame():
        path = filedialog.askopenfilename(parent=root)
        gameUI : GameUI|None = None
        if not path:
            return
        try:
           gameUI = GameFactory.LoadGameFromConfig(path)
        except LoadFailedException as e:
            messagebox.showwarning("Warning", str(e), parent=root)
        else:
            assert gameUI is not None
            root.destroy()
            gameUI.Play()
    
    btn = tk.Button(root, text="Load game configuration file", command=openGame)
    btn.pack(expand=True)

    root.mainloop()


def test2():
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "barchart.test.toml"
    a = GameFactory.LoadGameFromConfig(str(config_path))
    a.Play()


def test4():
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "linechart.test.toml"
    a = GameFactory.LoadGameFromConfig(str(config_path))
    a.Play()

def test5():
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "candlestick.test.toml"
    a = GameFactory.LoadGameFromConfig(str(config_path))
    a.Play()

def test6():
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "histogram.test.toml"
    a = GameFactory.LoadGameFromConfig(str(config_path))
    a.Play()

if __name__ == "__main__":
    StartGame()
