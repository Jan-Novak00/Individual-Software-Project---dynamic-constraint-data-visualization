import tkinter as tk
from tkinter import messagebox, filedialog
from predictiongame import GameFactory, GameUI, LoadFailedException
from tomllib import TOMLDecodeError


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
            messagebox.showerror("Error: invalid format", str(e), parent=root)
        except TOMLDecodeError as e:
            messagebox.showerror("Error: not TOML",str(e),parent=root)
        except Exception as e:
            messagebox.showerror("Error: unknown error",f"Unknown error has occured while loading the configuration file.\nError message:\n{str(e)}",parent=root)
            raise e
        else:
            assert gameUI is not None
            root.destroy()
            gameUI.Play()
    
    btn = tk.Button(root, text="Load game configuration file", command=openGame)
    btn.pack(expand=True)

    root.mainloop()

if __name__ == "__main__":
    StartGame()
