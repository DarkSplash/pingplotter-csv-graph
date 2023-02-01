import graph

import os
import tkinter as tk
import tkinter.ttk as ttk

from tkinter.filedialog import askopenfile

root = 0                                                # Initializing global GUI variables to some bogus value
frame = 0



def changeCSVFile(filename:str):
    """
    Used in guiSelectFilename()
    """
    graph.setGlobalFilename(filename)                   # Changing filename in graph script
    graph.csvInit()                                     # Creating formattedData.csv



def guiSelectFilename():
    """
    Prompts the user to select what .csv file they want to use via a GUI
    """
    global root                                         # Used to rename the window title
    stringPath = f"{os.getcwd()}"

    file = askopenfile(mode ='r', initialdir=stringPath, filetypes =[('Comma Separated Value', '*.csv')])
    if file is not None:
        changeCSVFile(file.name)
    file.close()

    if root != 0:                                       # Making sure this doesn't run when root hasn't been initialized yet
        setWindowTitle(root, f"PingPlotter CSV Grapher - {graph.getGlobalFilename().split('/')[-1]}") # Set window title to new filename



###############################################################################
#                                TKINTER LOGIC                                #
###############################################################################
def initRoot():
    global root
    root = tk.Tk()
    setWindowTitle(root, f"PingPlotter CSV Grapher - {graph.getGlobalFilename().split('/')[-1]}")
    root.geometry("400x400")
    root.focus_force()



def setWindowTitle(root, title:str):
    """
    Quick little function to rename the root window title
    """    
    root.title(title)



def frameKiller(*args):
    """
    Takes any number of frame arguments and iterates through them all and destroys them all
    """
    global frame
    frame.destroy()

    for argFrame in args:
        if isinstance(argFrame[0], tk.Frame):           # Checks to make sure that frames were actually passed
            argFrame[0].destroy()



def returnToHome(*args):                                
    frameKiller(args)                                   # Kills the current frame and any other frames passed to it and re-runs the logic for the main menu frame
    homeWindow()



def getHostnameMask(frame):
    hostnameMask = []

    for widget in frame.winfo_children():               # Starting all of the checkboxes unselected
        if isinstance(widget, tk.Checkbutton):
            hostnameMask.append(widget.var.get())

    return hostnameMask



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

    label = tk.Label(frame, text="Graph Specific Hosts")
    label.place(anchor = tk.CENTER, relx = .5, y = 10)

    backButton = ttk.Button(bottomFrame, text="Back",command=lambda: returnToHome(bottomFrame)) # Need lambda to call function w/ parameter and not have it execute on runtime
    backButton.grid(row=0, column=0, sticky="W")
    
    graphButton = ttk.Button(bottomFrame, text="Graph Selected",command=lambda: graph.csvInitSpecific(getHostnameMask(frame)))
    graphButton.grid(row=0, column=1, sticky="E")

    hostnameArr = graph.getHostname(graph.csvHostInformation(graph.filename))

    row = 1
    for hostname in hostnameArr:
        tempBool = tk.BooleanVar()
        tempBool.set(False)

        tempCheck = tk.Checkbutton(frame, text=hostname, variable=tempBool)# Adding a tk checkbox per hostname
        tempCheck.var = tempBool

        tempCheck.grid(row=row, sticky="W")             # Left justified, and starts at index 1 since 0 is a buffer
        row = row + 1
    
    for widget in frame.winfo_children():               # Starting all of the checkboxes unselected
        if isinstance(widget, tk.Checkbutton):
            widget.deselect()



def homeWindow():
    global frame
    frame = tk.Frame(root)
    frame.pack()

    label = ttk.Label(frame, text="Graph Selector")
    label.place(anchor=tk.CENTER, relx=.5, y=10)

    frame.grid_rowconfigure(0, minsize=25)

    button = ttk.Button(frame, text="Graph All Hosts", command=lambda: graph.graphAll(graph.getDataFrame()))
    button.grid(row=1, column=0)

    button2 = ttk.Button(frame, text="Graph Specific Hosts", command=lambda: specificHostsWindow())
    button2.grid(row=2, column=0)

    button3 = ttk.Button(frame, text="Change CSV File", command=lambda: guiSelectFilename())
    button3.grid(row=3, column=0)

    button4 = ttk.Button(frame, text="Current Filename", command=lambda: print(graph.getGlobalFilename()))
    button4.grid(row=4, column=0)

    root.mainloop()



def main():
    initRoot(graph.getGlobalFilename())
    homeWindow()



def test():
    guiSelectFilename()

    initRoot()
    homeWindow()



if __name__ == "__main__":
    test()