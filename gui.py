import graph

from tkinter import *
from tkinter.ttk import *

root = 0                                                # Initializing global GUI variables to some bogus value
frame = 0

def labelRename(lbl:Label, newString:str):
    lbl.configure(text=newString)



def addMenu(root):
    menu = Menu(root)
    item = Menu(menu)
    item.add_command(label='Back to Main Menu', command=lambda: home())
    item.add_command(label='Exit', command=lambda: root.destroy())
    menu.add_cascade(label='Menu', menu=item)
    root.config(menu=menu)



def home():
    """
    Function to kill the current tkinter frame and go back to the main menu
    """
    global frame
    frame.destroy()
    mainMenu()



def specificHosts():
    global frame
    frame.destroy()

    frame = Frame(root)
    frame.pack()

    label = Label(frame, text ="Graph Specific Hosts")
    label.place(anchor = CENTER, relx = .5, y = 7)

    hostnameArr = graph.getHostname(graph.csvHostInformation(graph.filename))

    frame.grid_rowconfigure(0, minsize=25)

    row = 1
    for hostname in hostnameArr:
        tempCheck = Checkbutton(frame, text=hostname)               # Adding a checkbox per hostname
        tempCheck.grid(row=row, sticky="W")                         # First row need to be blank for label header
        row = row + 1
    
    for widget in frame.winfo_children():
        print(type(widget))
        if isinstance(widget, Checkbutton):
            widget.set(0)
    
    print(frame.winfo_children())



def initRoot():
    global root
    root = Tk()
    root.title("PingPlotter CSV Grapher")
    root.geometry("350x400")
    addMenu(root)



def mainMenu():
    global frame
    frame = Frame(root)
    frame.pack()

    label = Label(frame, text ="Graph Selector")
    label.place(anchor = CENTER, relx = .5, y = 7)

    frame.grid_rowconfigure(0, minsize=25)

    button = Button(frame, text ='Graph All Hosts',command=lambda: graph.graphAll(graph.getDataFrame())) # Need lambda to call function w/ parameter and not have it execute on runtime
    button.grid(row=1, column=0)

    button2 = Button(frame, text ='Graph Specific Hosts',command=lambda: specificHosts())
    button2.grid(row=2, column=0)

    button3 = Button(frame, text ='Current Filename',command=lambda: print(graph.getGlobalFilename()))
    button3.grid(row=3, column=0)

    root.mainloop()



def main():
    initRoot()
    mainMenu()

def test():
    print(graph.getGlobalFilename())
    graph.setGlobalFilename("2023-01-30 cdns01.comcast.net ATLASNOVUS.csv")
    print(graph.getGlobalFilename())
    graph.csvInit()
    
    initRoot()
    mainMenu()



if __name__ == "__main__":
    test()