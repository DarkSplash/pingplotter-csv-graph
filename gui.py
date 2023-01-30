from tkinter import *
from tkinter.ttk import *

def labelRename(lbl:Label, newString:str):
    lbl.configure(text=newString)


def restart(root):
    root.destroy()
    main()


def main():
    root = Tk()
    root.title("PingPlotter CSV Grapher")
    root.geometry("300x300")

    menu = Menu(root)
    item = Menu(menu)
    item.add_command(label='Back to Main Menu', command=lambda: restart(root))
    menu.add_cascade(label='Menu', menu=item)
    root.config(menu=menu)

    label = Label(root, text ="Graph Selector")
    label.grid()

    button = Button(root, text ='Graph All Hops',command=lambda: labelRename(lbl=label, newString="a")) # Need lambda to call function w/ parameter and not have it execute on runtime
    button.grid()

    root.mainloop()


if __name__ == "__main__":
    main()