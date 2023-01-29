import plotly.express as px
import pandas as pd

hostArray = []                                          # Global Host Information variable

def csvHostInformation(filename:str):
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
                


def formatNewCSV(filename:str, totalHops:int):
    """
    Function takes PingPlotter CSV file and properly serializes the data portion
    to have correct headers so pandas can properly import it
    """
    
    ppCSV = open(filename, 'r', encoding='utf-8-sig')   # PingPlotter CSV file
    startLine = totalHops + 1                           # CSV ping data starts a bit after Host Info, this is the line in the file to start on
    
    csvHeader = "Datetime,"
    for hopNum in range(1, totalHops+1):                # Running through 1 - totalHops    
        if hopNum is not totalHops:
            csvHeader = csvHeader + f"{hostArray[hopNum-1]['hostname']},"
        else:                                           # Last CSV header cannot have comma at end of string
            csvHeader = csvHeader + f"{hostArray[hopNum-1]['hostname']}\n"

    tempCSVOverwrite = open("temp.csv", "w")
    tempCSVOverwrite.write(csvHeader)
    tempCSVOverwrite.close()

    tempCSV = open("temp.csv", "a")                     # Write the latency CSV data to this temp file
    for lineNumber, line in enumerate(ppCSV):
        if lineNumber > startLine:
            tempCSV.write(line)
    
    tempCSV.close()



def main():
    filename = "one.one.one.one ATLASNOVUS.csv"

    csvHostInformation(filename)
    
    totalHops = len(hostArray)
    formatNewCSV(filename, totalHops)
    
    df = pd.read_csv("temp.csv")

    fig = px.line(df, x='Datetime', y=df.columns, title="PingPlotter CSV Grapher")
    fig.update_layout(autotypenumbers='convert types')  # Converting string numbers to their proper types
    fig.update_xaxes(rangeslider_visible=True)
    fig.show()



if __name__ == "__main__":
    main()