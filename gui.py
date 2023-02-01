import graph

import tkinter as tk
import tkinter.ttk as ttk

from tkinter.filedialog import askopenfile

root = 0                                                # Initializing global GUI variables to some bogus value
frame = 0

###############################################################################
#                                TKINTER LOGIC                                #
###############################################################################
def frameKiller(*args):
    global frame
    frame.destroy()

    for argFrame in args:
        if isinstance(argFrame[0], tk.Frame):           # Checks to make sure that frames were actually passed
            argFrame[0].destroy()


###############################################################################
#                                 MENU LOGIC                                  #
###############################################################################
def returnToHome(*args):                                
    frameKiller(args)                                   # Kills the current frame and any other frames passed to it and re-runs the logic for the main menu frame
    homeWindow()



def addMenu(root):                                      # TODO: Figure out a way to also add the Main Menu just a menu button as well
    menu = tk.Menu(root)
    item = tk.Menu(menu)
    item.add_command(label="Back to Main Menu", command=lambda: returnToHome())
    item.add_command(label="Exit", command=lambda: root.destroy())
    menu.add_cascade(label="Menu", menu=item)
    root.config(menu=menu)



def initRoot():
    global root
    root = tk.Tk()
    root.title("PingPlotter CSV Grapher")
    root.geometry("350x400")
    # addMenu(root)



###############################################################################
#                                WINDOW LOGIC                                 #
###############################################################################
def specificHostsWindow():
    global frame
    frame.destroy()                                     # Killing Old frame

    frame = tk.Frame(root)
    frame.pack()

    bottomFrame = tk.Frame(root)
    bottomFrame.pack(side = tk.BOTTOM)

    frame.grid_rowconfigure(0, minsize=25)              # Label buffer
    bottomFrame.grid_rowconfigure(1, minsize=15)        # Bottom buttons buffer

    label = tk.Label(frame, text ="Graph Specific Hosts")
    label.place(anchor = tk.CENTER, relx = .5, y = 10)

    backButton = ttk.Button(bottomFrame, text ="Back",command=lambda: returnToHome(bottomFrame)) # Need lambda to call function w/ parameter and not have it execute on runtime
    backButton.grid(row = 0, sticky="W")

    hostnameArr = graph.getHostname(graph.csvHostInformation(graph.filename))

    row = 1
    for hostname in hostnameArr:
        tempCheck = tk.Checkbutton(frame, text=hostname)# Adding a tk checkbox per hostname
        tempCheck.grid(row=row, sticky="W")             # Left justified, and starts at index 1 since 0 is a buffer
        row = row + 1
    
    for widget in frame.winfo_children():               # Starting all of the checkboxes unselected
        if isinstance(widget, tk.Checkbutton):
            widget.deselect()



def homeWindow():
    global frame
    frame = tk.Frame(root)
    frame.pack()

    label = ttk.Label(frame, text ="Graph Selector")
    label.place(anchor = tk.CENTER, relx = .5, y = 10)

    frame.grid_rowconfigure(0, minsize=25)

    button = ttk.Button(frame, text ="Graph All Hosts",command=lambda: graph.graphAll(graph.getDataFrame())) # Need lambda to call function w/ parameter and not have it execute on runtime
    button.grid(row=1, column=0)

    button2 = ttk.Button(frame, text ="Graph Specific Hosts",command=lambda: specificHostsWindow())
    button2.grid(row=2, column=0)

    button3 = ttk.Button(frame, text ="Current Filename",command=lambda: print(graph.getGlobalFilename()))
    button3.grid(row=3, column=0)

    root.mainloop()



def main():
    initRoot()
    homeWindow()



def test():
    print(graph.getGlobalFilename())
    graph.setGlobalFilename("2023-01-30 cdns01.comcast.net ATLASNOVUS.csv")
    print(graph.getGlobalFilename())
    graph.csvInit()
    
    initRoot()
    homeWindow()



if __name__ == "__main__":
    test()