import graph

import os
import tkinter as tk
import tkinter.ttk as ttk

from tkinter.filedialog import askopenfile

root = 0                                                # Initializing global GUI variables to some bogus value
frame = 0                                               # Ideally it looks like python Classes should be used for GUIs instead of global vars, but since this is my first GUI project, it's staying simple
avg = 15                                                # Setting avg to default value in case user closes out of popup before defining avg


def setAvg(num:str, popup:tk.Toplevel):
    """
    Function used in popupAverage() to set the global avg variable to a new value
    and after setting the new value, destroys the popup window.

    Parameters
    ----------
    num : str
        String recieved from tkinter Entry widget which will be set equal to avg unless
        num is "0" or "", in which case a default of 15 is set.
    popup : Toplevel
        The tkinter popup window that asks you to set avg, will be destroyed at the end
        of this function.
    """
    global avg
    
    if num != '' and num != '0':
        avg = int(num)
    elif num == '0':
        print("Hop number cannot be zero, setting to default of 15 hops")
        avg = 15
    else:
        print("Blank number selected, setting to default of 15 hops")
        avg = 15
    
    popup.destroy()



def guiSelectFilename():
    """
    Function to prompt the user to select what .csv file they want to use via a GUI.
    Is literally the first function ran at runtime, since filename is used everywhere else.
    """
    global root                                         # Used to rename the window title
    stringPath = f"{os.getcwd()}"

    file = askopenfile(mode ='r', initialdir=stringPath, filetypes =[('Comma Separated Value', '*.csv')])
    if file is not None:
        graph.setGlobalFilename(file.name)              # Setting the new filename in graph.py's global filename variable
    file.close()

    if root != 0:                                       # Making sure this doesn't run if root hasn't been initialized yet
        setWindowTitle(root, f"PingPlotter CSV Grapher - {graph.getGlobalFilename().split('/')[-1]}") # Set window title to new filename



###############################################################################
#                                TKINTER LOGIC                                #
###############################################################################
def initRoot():
    """
    Function to initalize the root Tk variable and name the window appropriately.
    """
    global root
    root = tk.Tk()
    setWindowTitle(root, f"PingPlotter CSV Grapher - {graph.getGlobalFilename().split('/')[-1]}")
    root.geometry("400x400")
    root.focus_force()



def setWindowTitle(root:tk.Tk, title:str):
    """
    Function to rename the root window title. Used in initRoot() and guiSelectFilename().

    Parameters
    ----------
    root : Tk
        The root tkinter window that gets initialized by the Tk() function.
    title : str
        The new string you want to have as the window title.
    """    
    root.title(title)



def frameKiller(*args:tk.Frame):
    """
    Takes any number of frame arguments and iterates through them all and destroys them all.

    Parameters
    ----------
    *args : Frame
        Any number of tkinter Frames you wish to destroy.
    """
    global frame
    frame.destroy()

    for argFrame in args:
        if isinstance(argFrame[0], tk.Frame):           # Checks to make sure that frames were actually passed
            argFrame[0].destroy()



def returnToHome(*args:tk.Frame):
    """
    Function to destroy all currently used tkinter frames and then return to the home
    window where you can make more graph selections.

    Parameters
    ----------
    *args : Frame
        Any number of tkinter Frames you wish to destroy.
    """
    frameKiller(args)                                   # Kills the current frame and any other frames passed to it and re-runs the logic for the main menu frame
    homeWindow()



def getHostnameMask(frame:tk.Frame) -> list:
    """
    Function to figure out what ttk.Checkbuttons have been selected in a given
    tkinter frame. Returns a list of 0's and 1's in a 1:1 relationship with the
    hostnames for each hop. 0 means don't include the host in the graph, while 1
    means do include this host in the graph.

    Parameters
    ----------
    frame : Frame
        The tkinter frame from specificHostsWindow() that holds all the Checkbutton widgets.
    
    Returns
    -------
    hostnameMask : list
        A list containing 0's and 1's, with the indexes representing each hop from 
        PingPlotter (0 indexed). 1 means include in graph, 0 means do not graph.
    """
    hostnameMask = []

    for widget in frame.winfo_children():
        if isinstance(widget, ttk.Checkbutton):
            if widget.instate(['selected']):            # For some reason Linux does not like widget.var.get() (was always False), so checking widget state instead
                hostnameMask.append(True)
            else:
                hostnameMask.append(False)
    print(hostnameMask)
    return hostnameMask



def onlyInt(inStr, acttyp):
    """
    Function from https://stackoverflow.com/a/35554720 to only allow digits 
    into tkinter entry fields. Used in popupAverage().
    """
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True



###############################################################################
#                                WINDOW LOGIC                                 #
###############################################################################
def homeWindow():
    """
    Function that contains all the tkinter GUI logic for the main menu/home window.
    """
    global frame
    frame = tk.Frame(root)
    frame.pack()

    label = ttk.Label(frame, text="Graph Selector")
    label.place(anchor=tk.CENTER, relx=.5, y=10)

    frame.grid_rowconfigure(0, minsize=25)

    button = ttk.Button(frame, text="Graph All Hosts", command=lambda: graph.graphAll())
    button.grid(row=1, column=0)

    button2 = ttk.Button(frame, text="Graph Specific Hosts", command=lambda: specificHostsWindow())
    button2.grid(row=2, column=0)

    button3 = ttk.Button(frame, text="Graph Single Host", command=lambda: singleHostWindow())
    button3.grid(row=3, column=0)
    
    button4 = ttk.Button(frame, text="Change CSV File", command=lambda: guiSelectFilename())
    button4.grid(row=4, column=0)

    button5 = ttk.Button(frame, text="Current Filename", command=lambda: print(graph.getGlobalFilename()))
    button5.grid(row=5, column=0)

    root.mainloop()



def specificHostsWindow():
    """
    Function that contains all the tkinter GUI logic for graphing specific hosts.
    """
    global frame
    frame.destroy()                                     # Killing Old frame

    frame = tk.Frame(root)
    frame.pack()

    bottomFrame = tk.Frame(root)
    bottomFrame.pack(side = tk.BOTTOM)

    frame.grid_rowconfigure(0, minsize=25)              # Label buffer
    bottomFrame.grid_rowconfigure(1, minsize=15)        # Bottom buttons buffer

    label = ttk.Label(frame, text="Graph Specific Hosts")
    label.place(anchor = tk.CENTER, relx = .5, y = 10)

    backButton = ttk.Button(bottomFrame, text="Back",command=lambda: returnToHome(bottomFrame))
    backButton.grid(row=0, column=0, sticky="W")
    
    graphButton = ttk.Button(bottomFrame, text="Graph Selected",command=lambda: graph.graphSpecific(getHostnameMask(frame)))
    graphButton.grid(row=0, column=1, sticky="E")

    hostnameArr = graph.getHostname(graph.csvHostInformation(graph.filename))

    row = 1
    for hostname in hostnameArr:
        tempCheck = ttk.Checkbutton(frame, text=hostname)  # Adding a ttk checkbox per hostname

        tempCheck.grid(row=row, sticky="W")             # Left justified, and row starts at index 1 since 0 is a buffer
        row = row + 1
    
    for widget in frame.winfo_children():               # Starting all of the checkboxes unselected
        if isinstance(widget, ttk.Checkbutton):
            widget.invoke()
            widget.invoke()                             # Double select to turn on, then off



def popupAverage():
    """
    Function used in singleHostWindow() to open a popup window and allow the user to set
    the global avg value.
    """

    popup = tk.Toplevel(root)
    popup.geometry("200x100")
    popup.focus_force()

    label = ttk.Label(popup, text="Number of pings used to calculate\njitter and moving average", justify="center")
    label.pack()

    entry = ttk.Entry(popup, validate="key")            # Code from https://stackoverflow.com/a/35554720
    entry['validatecommand'] = (entry.register(onlyInt),'%P','%d')  # Makes it so only digits are accepted into this entry field
    entry.pack()

    button = ttk.Button(popup, text="Set",command=lambda: setAvg(entry.get(), popup))
    button.pack()




def singleHostWindow():
    """
    Function that contains all the tkinter GUI logic for graphing a single host.
    """
    global frame
    global avg
    frame.destroy()                                     # Killing Old frame

    popupAverage()

    frame = tk.Frame(root)
    frame.pack()

    bottomFrame = tk.Frame(root)
    bottomFrame.pack(side = tk.BOTTOM)

    frame.grid_rowconfigure(0, minsize=25)              # Label buffer
    bottomFrame.grid_rowconfigure(1, minsize=15)        # Bottom buttons buffer

    label = ttk.Label(frame, text="Graph Single Host")
    label.place(anchor = tk.CENTER, relx = .5, y = 10)

    backButton = ttk.Button(bottomFrame, text="Back",command=lambda: returnToHome(bottomFrame))
    backButton.grid(row=0, column=0, sticky="W")
    
    graphButton = ttk.Button(bottomFrame, text="Graph Host",command=lambda: graph.graphSingle(hostnameArr[radioSelection.get()], avg))  # Passing needed vars over to graph.py
    graphButton.grid(row=0, column=1, sticky="E")

    hostnameArr = graph.getHostname(graph.csvHostInformation(graph.filename))

    radioSelection = tk.IntVar()                        # Variable that will hold the index of the selected hostname from hostnameArr
    row = 1
    for hostname in hostnameArr:
        tempCheck = ttk.Radiobutton(frame, text=hostname, variable=radioSelection, value=row-1)# Adding a ttk radiobutton per hostname, value coincides with hostnameArr indexes

        tempCheck.grid(row=row, sticky="W")             # Left justified, and row starts at index 1 since 0 is a buffer
        row = row + 1



def main():
    guiSelectFilename()                                 # Selecting the PingPlotter .csv export
    initRoot()                                          # Initializing the tkinter root window
    homeWindow()                                        # Loading the main menu frame



if __name__ == "__main__":
    main()