from tkinter import *
from tkinter.ttk import *

def main():
    root = Tk()
    root.geometry("300x300")
    root.title("PingPlotter CSV Grapher")
    
    frame = Frame(root)
    frame.grid()    
    
    label = Label(root, text ="Graph Selector").grid()

    button = Button(frame, text ='Graph All Hops') 
    button.grid()     
    
    root.mainloop()


if __name__ == "__main__":
    main()