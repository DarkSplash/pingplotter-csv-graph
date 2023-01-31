import plotly.express as px
import pandas as pd

filename = "2023-01-29 one.one.one.one ATLASNOVUS trim.csv"
# filename = "2023-01-30 cdns01.comcast.net ATLASNOVUS.csv"

def getGlobalFilename() -> str:
    global filename
    return filename



def setGlobalFilename(newFilename:str):
    global filename
    filename = newFilename



def csvHostInformation(filename:str):   
    hostArray = []

    with open(filename, 'r', encoding='utf-8-sig') as csv:  # PingPlotter CSV file
        for line in csv:                                # Grabbing the Host Information section of data
            if "Sample Information" in line:
                break
            elif "Host Information" in line:
                pass
            else:
                lineData = line.strip()
                lineData = lineData.split(",")
                
                hostDict = {}                           # Dict = {'hop':'1', 'hostname':'testaroni.net', 'ip':'1.2.3.4'}
                hostDict["hop"] = lineData[0]
                hostDict["hostname"] = lineData[1]
                hostDict["ip"] = lineData[2]
                hostArray.append(hostDict)
    
    return hostArray
                


def formatNewCSV(filename:str, totalHops:int, hostArray):
    """
    Function takes PingPlotter CSV file and properly serializes the data portion
    to have correct headers so pandas can properly import it
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

    tempCSV = open("formattedData.csv", "a")                     # Write the latency CSV data to this temp file
    for lineNumber, line in enumerate(ppCSV):
        if lineNumber > startLine:
            tempCSV.write(line)
    
    tempCSV.close()
    ppCSV.close()



def csvInit():
    hostArray = csvHostInformation(filename)
    totalHops = len(hostArray)
    formatNewCSV(filename, totalHops, hostArray)



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



def graphAll(df):
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
    csvInit()

    df = getDataFrame()

    graphAll(df)



if __name__ == "__main__":
    main()