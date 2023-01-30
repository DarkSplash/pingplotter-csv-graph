import graph

from tkinter import *
from tkinter.ttk import *

def labelRename(lbl:Label, newString:str):
    lbl.configure(text=newString)


def addMenu(root):
    menu = Menu(root)
    item = Menu(menu)
    item.add_command(label='Back to Main Menu', command=lambda: restart(root))
    menu.add_cascade(label='Menu', menu=item)
    root.config(menu=menu)


def restart(root):
    """
    Function to kill the current tkinter root window and recall the main method
    """
    root.destroy()
    mainMenu()



def mainMenu():
    root = Tk()
    root.title("PingPlotter CSV Grapher")
    root.geometry("300x300")

    addMenu(root)

    label = Label(root, text ="Graph Selector")
    label.grid()

    button = Button(root, text ='Graph All Hops',command=lambda: graph.graphAll(graph.getDataFrame())) # Need lambda to call function w/ parameter and not have it execute on runtime
    button.grid()

    root.mainloop()



def main():
    mainMenu()



if __name__ == "__main__":
    main()