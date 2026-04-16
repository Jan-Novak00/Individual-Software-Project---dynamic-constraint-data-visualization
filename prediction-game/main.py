from kiwiplots import *
from predictiongame import *
from tkinter import messagebox
BASE_DIR = Path(__file__).resolve().parent

def test1():
    a = GameFactory.BarChartGameTEST()
    a.Play()

def test2():
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "barchart.test.toml"
    a = GameFactory.LoadGameFromConfig(str(config_path))
    a.Play()

def test3():
    a = GameFactory.LineChartGameTEST()
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

if __name__ == "__main__":
    test2()
