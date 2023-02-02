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
                


def formatNewCSV(filename:str, totalHops:int, hostArray):
    """
    Used in csvInit()). Function takes PingPlotter CSV file and properly serializes
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



def formatNewCSVSpecific(filename:str, totalHops:int, hostArray:list, hostnameMask:list):
    """
    Used in csvInitSpecific(). Function takes the hostname mask from gui.getCheckboxStatus()
    and only selects the respective columns that were set to True in the mask while performing
    similar serialization tasks that formatNewCSV() also does.
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



def csvInit():
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSV(filename, totalHops, hostArray)



def csvInitSpecific(hostnameMask:list):
    """
    Used in gui.specificHostsWindow() to make a .csv file with only whatever hostnames
    were selected in the GUI.
    """
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSVSpecific(filename, totalHops, hostArray, hostnameMask)



def getDataFrame():
    """
    Assumes the .csv file is named formattedData.csv thanks to formatNewCSV()
    """
    df = pd.read_csv("formattedData.csv")
    df = df.astype(object)                              # Need to explicitly cast all columns to one type or else Plotly will complain
    return df



def getHostname(hostArray):
    hostnameArr = []
    for dict in hostArray:
        hostnameArr.append(dict["hostname"])
    
    return hostnameArr



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
    
    fig.show()



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
    
    fig.show()



def main():
    graphAll()



if __name__ == "__main__":
    main()