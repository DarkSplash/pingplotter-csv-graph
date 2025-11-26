import plotly.express as px
import pandas as pd
import re

filename = ""                                           # Global variable that holds path to the PingPlotter .csv export you want to graph



def getGlobalFilename() -> str:
    """
    Getter function for global filename variable that is used a few time in gui.py.

    Returns
    -------
    filename : str
        String containing a path to the selected PingPlotter .csv file.
    """
    global filename
    return filename



def setGlobalFilename(newFilename:str):
    """
    Setter function for global filename variable that is used in gui.guiSelectFilename().

    Parameters
    ----------
    newFilename : str
        String containing a path to the newly selected PingPlotter .csv file.
    """
    global filename
    filename = newFilename



def csvHostInformation(filename:str) -> list:
    """
    Function to create a list of dicts with the host information from each hop from PingPlotter.
    The host list looks something like this:\n\n
    
    hostArray = [
        {'hop':'1', 'hostname':'test.net', 'ip':'1.2.3.4'},
        {'hop':'2', 'hostname':'one.one.one.one', 'ip':'1.1.1.1'}
    ]

    Returns
    -------
    hostArray : list
        An array that contains all of the host information in the capture.
    """
    hostArray = []

    with open(filename, 'r', encoding='utf-8-sig') as csv:  # PingPlotter CSV file
        for line in csv:                                # Grabbing the Host Information section of data
            if "Sample Information" in line:
                break
            elif "Host Information" in line:
                pass
            else:
                lineData = line.strip()                 # Stripping all newline escape characters out of strings
                lineData = lineData.split(",")
                
                hostDict = {}                           # Dict = {'hop':'1', 'hostname':'testaroni.net', 'ip':'1.2.3.4'}
                hostDict["hop"] = lineData[0]
                hostDict["hostname"] = lineData[1]
                hostDict["ip"] = lineData[2]
                if hostDict["hostname"] == "":
                    hostDict["hostname"] = f"Unknown[{hostDict['hop']}]"
                if hostDict["ip"] == "-":
                    hostDict["ip"] = f"Unknown[{hostDict['hop']}]"
                hostArray.append(hostDict)
    
    return hostArray
                


def getDataFrame() -> pd.DataFrame:
    """
    Function to create a pandas dataframe from a pre-formatted .csv file called
    formattedData.csv that gets created from the numerous formatNewCSV... functions.
    
    Returns
    -------
    df : DataFrame
        A pandas Dataframe for the plotly graphing library to create a time series line graph with.
    """
    df = pd.read_csv("formattedData.csv")
    df = df.astype(object)                              # Need to explicitly cast all columns to one type or else Plotly will complain
    return df



def getHostname(hostArray:list) -> list:
    """
    Function that is used in gui.specificHostsWindow() and gui.singleHostWindow()
    to list out all hostnames that need checkboxes/radiobuttons.

    Returns
    -------
    hostnameArr : list
        A list of all hostnames from the currently selected PingPlotter CSV file.
    """
    hostnameArr = []
    for dict in hostArray:
        hostnameArr.append(dict["hostname"])
    
    return hostnameArr

###############################################################################
#                               ALL HOSTS LOGIC                               #
###############################################################################
def formatNewCSV(filename:str, totalHops:int, hostArray:list):
    """
    Final function call in graph.py in function chain that looks like so:

    gui.homeWindow() -> graphAll() -> csvInit() -> formatNewCSV()

    This is the function that creates the CSV file that contains the data that gets plotted
    in graphSpecific(). This function figures out how many hostnames you have selected in your
    hostnameMask, and then iterates through each CSV line and only selects the data from the 
    hosts you selected with some simple index math.

    Parameters
    ----------
    filename : str
        The filename of the PingPlotter .csv file.
    totalHops : int
        Integer that holds the total number of hops to your target. Used to let the user know
        what hop they selected when graphing, and is also used to select the first row of actual
        ping data in the PingPlotter .csv file, since their export starts with host information.
    hostArray : list
        An array that contains all of the host information in the capture, Used here to grab hop
        hostnames. Look at csvHostInformation() for more information.
    """
    
    ppCSV = open(filename, 'r', encoding='utf-8-sig')   # PingPlotter CSV file
    startLine = totalHops + 1                           # CSV ping data starts a bit after Host Info, this is the line in the file to start on
    
    csvHeader = "Datetime,"
    for hopNum in range(1, totalHops+1):                # Running through 1 - totalHops    
        if hopNum is not totalHops:
            csvHeader = csvHeader + f"{hopNum} - {hostArray[hopNum-1]['hostname']},"
        else:                                           # Last CSV header cannot have comma at end of string
            csvHeader = csvHeader + f"{hopNum} - {hostArray[hopNum-1]['hostname']}\n"

    tempCSVOverwrite = open("formattedData.csv", "w")
    tempCSVOverwrite.write(csvHeader)
    tempCSVOverwrite.close()

    tempCSV = open("formattedData.csv", "a")            # Write the PingPlotter CSV data to the newly formatted CSV
    for lineNumber, line in enumerate(ppCSV):
        if lineNumber > startLine:
            regex = re.sub(r'\bN/A\b|\*', '0', line)    # Checking for any instances of "N/A" or "*" and replacing them with 0
            tempCSV.write(regex)
    
    tempCSV.close()
    ppCSV.close()



def csvInit():
    """
    Second function call in graph.py in function chain that looks like so:

    gui.homeWindow() -> graphAll() -> csvInit() -> formatNewCSV()

    This is an intermediary function that sets up some variables that are needed
    in formatNewCSV().
    """
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSV(filename, totalHops, hostArray)



def graphAll():
    """
    Initial function call from gui.py in function chain that looks like so:

    gui.homeWindow() -> graphAll() -> csvInit() -> formatNewCSV()

    This is the function with the Plotly graphing logic in it, mostly identical to the
    other graph functions. The actual graphing logic happens after the new formattedData.csv
    file is created from formatNewCSV().
    """
    csvInit()
    df = getDataFrame()
    
    fig = px.line(df, x='Datetime', y=df.columns, title="PingPlotter CSV Grapher", line_shape="hv")
    fig.update_layout(autotypenumbers='convert types', yaxis_title="Ping (ms)") # Converting string numbers to their proper types & setting Y axis title
    fig.update_xaxes(
        tickformat="%I:%M %p\n%b %d, %Y",
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1min", step="minute", stepmode="backward"),
                dict(count=5, label="5min", step="minute", stepmode="backward"),
                dict(count=10, label="10min", step="minute", stepmode="backward"),
                dict(count=30, label="30min", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig.update_yaxes(
        fixedrange=False
    )

    fig.show()

###############################################################################
#                            SPECIFIC HOSTS LOGIC                             #
###############################################################################
def formatNewCSVSpecific(filename:str, totalHops:int, hostArray:list, hostnameMask:list):
    """
    Final function call in graph.py in function chain that looks like so:

    gui.specificHostsWindow() -> graphSpecific() -> csvInitSpecific() -> formatNewCSVSpecific()

    This is the function that creates the CSV file that contains the data that gets plotted
    in graphSpecific(). This function figures out how many hostnames you have selected in your
    hostnameMask, and then iterates through each CSV line and only selects the data from the 
    hosts you selected with some simple index math.

    Parameters
    ----------
    filename : str
        The filename of the PingPlotter .csv file.
    totalHops : int
        Integer that holds the total number of hops to your target. Used to let the user know
        what hop they selected when graphing, and is also used to select the first row of actual
        ping data in the PingPlotter .csv file, since their export starts with host information.
    hostArray : list
        An array that contains all of the host information in the capture, Used here to grab hop
        hostnames. Look at csvHostInformation() for more information.
    hostnameMask : list
        A list of hostnames that the user has selected to be graphed.
    """
    ppCSV = open(filename, 'r', encoding='utf-8-sig')   # PingPlotter CSV file
    startLine = totalHops + 1                           # CSV ping data starts a bit after Host Info, this is the line in the file to start on
    
    trueIndexes = [i for i, val in enumerate(hostnameMask) if val]  # Fancy one liner that finds all the indicies that are true in an array
    lastTrueIndex = trueIndexes[-1]                     # Getting the last index of true so I know not to add a comma to the end of the string
    trueIndexLength = len(trueIndexes)                  # Number of hosts selected to graph

    csvHeader = "Datetime,"
    for hopNum in range(1, totalHops+1):                # Running through 1 - totalHops    
        if hopNum is not totalHops and hostnameMask[hopNum-1] and hopNum is not (lastTrueIndex + 1):    # Adding 1 to lastTrueIndex since this loop starts at 1, not 0
            csvHeader = csvHeader + f"{hopNum} - {hostArray[hopNum-1]['hostname']},"
        elif hostnameMask[hopNum-1] and hopNum is (lastTrueIndex + 1):        # Last CSV header cannot have comma at end of string
            csvHeader = csvHeader + f"{hopNum} - {hostArray[hopNum-1]['hostname']}\n"                                          
            

    tempCSVOverwrite = open("formattedData.csv", "w")
    tempCSVOverwrite.write(csvHeader)
    tempCSVOverwrite.close()

    tempCSV = open("formattedData.csv", "a")            # Write the PingPlotter CSV data to the newly formatted CSV
    for lineNumber, line in enumerate(ppCSV):
        if lineNumber > startLine:                      # Iterating through all of the actual data (starting after Sample Information) in the PingPlotter CSV file
            stripedLine = line.strip()                  # Stripping all newline escape characters out of each line in file
            lineArray = stripedLine.split(",")          # Splitting up CSV line into list so I can mask out the hostnames not to be graphed

            newLine = f"{lineArray[0]},"                # Starting the variable for new line to be appended to formattedData.csv with the datetime from the current row of data

            for x in range(trueIndexLength):            # Looping for each of the hosts that have been selected
                csvDataIndex = trueIndexes[x] + 1       # Adding 1 to the index location of the csv data since the first CSV value is Datetime variable
                
                if lineArray[csvDataIndex] != "N/A" and lineArray[csvDataIndex] != "*":
                    newLine = newLine + lineArray[csvDataIndex] # Adding the data to the current line to be added to the new file
                else:
                    newLine = newLine + "0"             # If the current ping data is either N/A or *, replace it with the numeric value 0.  If this isn't done, Plotly will not be able to graph due to mixed string and numeric variable types

                if x != trueIndexLength - 1:            # If you are not on the last piece of data for this row
                    newLine = newLine + ","             # Add a comma
                else:
                    newLine = newLine + "\n"            # Otherwise newline
            
            tempCSV.write(newLine)                      # Write the new line CSV line with only the data from the selected hostnames

    tempCSV.close()
    ppCSV.close()



def csvInitSpecific(hostnameMask:list):
    """
    Second function call in graph.py in function chain that looks like so:

    gui.specificHostsWindow() -> graphSpecific() -> csvInitSpecific() -> formatNewCSVSpecific()

    This is an intermediary function that sets up some variables that are needed
    in formatNewCSVSpecific().

    Parameters
    ----------
    hostnameMask : list
        A list of hostnames that the user has selected to be graphed.
    """
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSVSpecific(filename, totalHops, hostArray, hostnameMask)



def graphSpecific(hostnameMask:list):
    """
    Initial function call from gui.py in function chain that looks like so:

    gui.specificHostsWindow() -> graphSpecific() -> csvInitSpecific() -> formatNewCSVSpecific()

    This is the function with the Plotly graphing logic in it, mostly identical to the
    other graph functions. The actual graphing logic happens after the new formattedData.csv
    file is created from formatNewCSVSpecific().

    Parameters
    ----------
    hostnameMask : list
        A list of hostnames that the user has selected to be graphed.
    """
    csvInitSpecific(hostnameMask)
    df = getDataFrame()
    
    fig = px.line(df, x='Datetime', y=df.columns, title="PingPlotter CSV Grapher", line_shape="hv")
    fig.update_layout(autotypenumbers='convert types', yaxis_title="Ping (ms)") # Converting string numbers to their proper types & setting Y axis title
    fig.update_xaxes(
        tickformat="%I:%M %p\n%b %d, %Y",
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1min", step="minute", stepmode="backward"),
                dict(count=5, label="5min", step="minute", stepmode="backward"),
                dict(count=10, label="10min", step="minute", stepmode="backward"),
                dict(count=30, label="30min", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig.update_yaxes(
        fixedrange=False
    )
    
    fig.show()

###############################################################################
#                              SINGLE HOST LOGIC                              #
###############################################################################
def formatNewCSVSingle(filename:str, totalHops:int, hostArray:list, hostname:str, avg:int):
    """
    Final function call in graph.py in function chain that looks like so:

    gui.singleHostWindow() -> graphSingle() -> csvInitSingle() -> formatNewCSVSingle()

    This is the function that creates the CSV file that contains the data that gets plotted
    in graphSingle(). For the single host csv, there are calculations to find the moving
    average and jitter over the last avg pings. Any pings that are "N/A" or "*" are set to
    0 ping.

    Parameters
    ----------
    filename : str
        The filename of the PingPlotter .csv file.
    totalHops : int
        Integer that holds the total number of hops to your target. Used to let the user know
        what hop they selected when graphing, and is also used to select the first row of actual
        ping data in the PingPlotter .csv file, since their export starts with host information.
    hostArray : list
        An array that contains all of the host information in the capture, Used here to grab hop
        hostnames. Look at csvHostInformation() for more information.
    hostname : str
        The hostname of the hop that is being singled out for graphing.
    avg : int
        An integer the user selects that determines how many hops are included in the 
        moving average and jitter calculations.
    """
    recentPings = []                                    # An array to hold the last x number of pings, with x being user defined
    jitter = []                                         # An array to hold the difference between the last two pings, mostly from https://www.pingman.com/kb/article/what-is-jitter-57.html
    
    ppCSV = open(filename, 'r', encoding='utf-8-sig')   # PingPlotter CSV file
    startLine = totalHops + 1                           # CSV ping data starts a bit after Host Info, this is the line in the file to start on

    csvHeader = "Datetime,"
    selectedHop = 0                                     # Variable for which hop was actually selected, will be used for data selection later in a 1 indexed dataset
    for hopNum in range(1, totalHops+1):                # Running through 1 - totalHops  
        if hostname == hostArray[hopNum-1]['hostname']:
            csvHeader = csvHeader + f"{hopNum} - {hostArray[hopNum-1]['hostname']},Moving Average for last {avg} pings, Jitter for last {avg} pings\n" 
            selectedHop = hopNum                                     

    tempCSVOverwrite = open("formattedData.csv", "w")
    tempCSVOverwrite.write(csvHeader)
    tempCSVOverwrite.close()

    tempCSV = open("formattedData.csv", "a")            # Write the PingPlotter CSV data to the newly formatted CSV
    for lineNumber, line in enumerate(ppCSV):
        if lineNumber > startLine:
            stripedLine = line.strip()                  # Stripping all newline escape characters out of each line in file
            lineArray = stripedLine.split(",")          # Splitting up CSV line into list so I can mask out the hostnames not to be graphed

            if lineArray[selectedHop] != "N/A" and lineArray[selectedHop] != "*":
                recentPings.append(float(lineArray[selectedHop]))
            else:
                lineArray[selectedHop] = 0              # If the current ping data is either N/A or *, replace it with the numeric value 0.  If this isn't done, Plotly will not be able to graph due to mixed string and numeric variable types
                recentPings.append(0)
            recentPings = recentPings[-avg:]            # Only keeping the last avg number of values in the array

            if len(recentPings) > 1:                    # Checking to see if there even is two elements to find the difference between
                jitter.append(abs(recentPings[-1]-recentPings[-2]))
            else:
                jitter.append(recentPings[-1])
            
            jitter = jitter[-(avg-1):]                  # Only keeping the last avg - 1 number of values in the array

            movingAverage = round(sum(recentPings) / len(recentPings), 2)  # Calculating the rolling average of the recent pings
            jitterAverage = round(sum(jitter) / len(jitter), 2) # Calculating the jitter of the recent pings

            newLine = f"{lineArray[0]},{lineArray[selectedHop]},{movingAverage},{jitterAverage}\n"  # Variable for new line to be appended to formattedData.csv with only single host
            tempCSV.write(newLine)                      # Write the new line CSV line with only the data from the selected host

    tempCSV.close()
    ppCSV.close()



def csvInitSingle(hostname:str, avg:int):
    """
    Second function call in graph.py in function chain that looks like so:

    gui.singleHostWindow() -> graphSingle() -> csvInitSingle() -> formatNewCSVSingle()

    This is an intermediary function that sets up some variables that are needed
    in formatNewCSVSingle().

    Parameters
    ----------
    hostname : str
        The hostname of the hop that is being singled out for graphing.
    avg : int
        An integer the user selects that determines how many hops are included in the 
        moving average and jitter calculations.
    """
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSVSingle(filename, totalHops, hostArray, hostname, avg)



def graphSingle(hostname:str, avg:int):
    """
    Initial function call from gui.py in function chain that looks like so:

    gui.singleHostWindow() -> graphSingle() -> csvInitSingle() -> formatNewCSVSingle()

    This is the function with the Plotly graphing logic in it, mostly identical to the
    other graph functions. The actual graphing logic happens after the new formattedData.csv
    file is created from formatNewCSVSingle().

    Parameters
    ----------
    hostname : str
        The hostname of the hop that is being singled out for graphing.
    avg : int
        An integer the user selects that determines how many hops are included in the 
        moving average and jitter calculations.
    """
    csvInitSingle(hostname, avg)
    df = getDataFrame()
    
    fig = px.line(df, x='Datetime', y=df.columns, title="PingPlotter CSV Grapher", line_shape="hv")
    fig.update_layout(autotypenumbers='convert types', yaxis_title="Ping (ms)") # Converting string numbers to their proper types & setting Y axis title
    fig.update_xaxes(
        tickformat="%I:%M %p\n%b %d, %Y",
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1min", step="minute", stepmode="backward"),
                dict(count=5, label="5min", step="minute", stepmode="backward"),
                dict(count=10, label="10min", step="minute", stepmode="backward"),
                dict(count=30, label="30min", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig.update_yaxes(
        fixedrange=False
    )
    
    fig.show()