import plotly.express as px
import pandas as pd

# filename = ""
filename = "2023-01-29 one.one.one.one ATLASNOVUS trim.csv"
# filename = "2023-01-30 cdns01.comcast.net ATLASNOVUS.csv"



def getGlobalFilename() -> str:
    global filename
    return filename



def setGlobalFilename(newFilename:str):
    global filename
    filename = newFilename



def csvHostInformation(filename:str):
    """
    Function creates a list of dicts with the host information from each hop from PingPlotter.
    The host list looks something like this:\n\n
    
    hostArray = [
        {'hop':'1', 'hostname':'test.net', 'ip':'1.2.3.4'},
        {'hop':'2', 'hostname':'one.one.one.one', 'ip':'1.1.1.1'}
    ]
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
                hostArray.append(hostDict)
    
    return hostArray
                


def getDataFrame():
    """
    Assumes the .csv file is named formattedData.csv thanks to the numerous format functions
    """
    df = pd.read_csv("formattedData.csv")
    df = df.astype(object)                              # Need to explicitly cast all columns to one type or else Plotly will complain
    return df



def getHostname(hostArray):
    hostnameArr = []
    for dict in hostArray:
        hostnameArr.append(dict["hostname"])
    
    return hostnameArr

###############################################################################
#                               ALL HOSTS LOGIC                               #
###############################################################################
def formatNewCSV(filename:str, totalHops:int, hostArray):
    """
    Used in csvInit(). Function takes PingPlotter CSV file and properly serializes
    the data portion to have correct headers so pandas can properly import it.
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
            tempCSV.write(line)
    
    tempCSV.close()
    ppCSV.close()



def csvInit():
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSV(filename, totalHops, hostArray)



def graphAll():
    csvInit()
    df = getDataFrame()
    
    fig = px.line(df, x='Datetime', y=df.columns, title="PingPlotter CSV Grapher", line_shape="hv")
    fig.update_layout(autotypenumbers='convert types')  # Converting string numbers to their proper types
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
        if lineNumber > startLine:                      # Iterating through all of the actual data in the PingPlotter CSV file
            stripedLine = line.strip()                  # Stripping all newline escape characters out of each line in file
            lineArray = stripedLine.split(",")          # Splitting up CSV line into list so I can mask out the hostnames not to be graphed

            newLine = f"{lineArray[0]},"                # Variable for new line to be appended to formattedData.csv with only selected hostnames

            for x in range(trueIndexLength):            # Looping for each of the hosts that have been selected
                csvDataIndex = trueIndexes[x] + 1       # Adding 1 to the index location of the csv data since the first CSV value is Datetime variable
                
                newLine = newLine + lineArray[csvDataIndex] # Adding the data to the current line to be added to the new file

                if x != trueIndexLength-1:              # If you are not on the last piece of data for this row
                    newLine = newLine + ","             # Add a comma
                else:
                    newLine = newLine + "\n"            # Otherwise newline
            
            tempCSV.write(newLine)                      # Write the new line CSV line with only the data from the selected hostnames

    tempCSV.close()
    ppCSV.close()



def csvInitSpecific(hostnameMask:list):
    """
    
    """
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSVSpecific(filename, totalHops, hostArray, hostnameMask)



def graphSpecific(hostnameMask:list):
    csvInitSpecific(hostnameMask)
    df = getDataFrame()
    
    fig = px.line(df, x='Datetime', y=df.columns, title="PingPlotter CSV Grapher", line_shape="hv")
    fig.update_layout(autotypenumbers='convert types')  # Converting string numbers to their proper types
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
                if lineNumber < startLine + 3:          # If you're within the first three pings and get a N/A or *, assume 0 ping so avg and jitter dont look like trash
                    recentPings.append(0)
                else:
                    recentPings.append(999)             # If the host has either dropped the connection completely or isn't responding, default to 999 ping
            recentPings = recentPings[-avg:]            # Only keeping the last avg number of values in the array

            if len(recentPings) > 1:                    # Checking to see if there even is two elements to average
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
    test 
    """
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSVSingle(filename, totalHops, hostArray, hostname, avg)



def graphSingle(hostname:str, avg:int):
    """
    Initial function call from gui.py in function chain that looks like so:

    gui.singleHostWindow() -> graphSingle() -> csvInitSingle() -> formatNewCSVSingle()

    Allows the user to select a single host, and then does some calcualtions to determine the
    moving average and the jitter of the last x pings, with x being user defined.

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
    fig.update_layout(autotypenumbers='convert types', )  # Converting string numbers to their proper types
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





def main():
    graphAll()



if __name__ == "__main__":
    main()