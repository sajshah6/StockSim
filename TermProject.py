import yfinance as yf
from cmu_112_graphics import *
from tkinter import *
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import make_dataclass
import copy

ProbCircles = make_dataclass("ProbCircles", ["cx", "cy", "r"])

def appStarted(app):
    app.title = 'StockSim'
    app.margin = 50
    app.rectangleHeight = 75
    app.rectangleWidth = 300
    app.x1 = 50
    app.y1 = 350
    app.mode = "titlePage"
    
    app.tickerFutureList = [ ]
    app.futureStocksBought = [ ]
    app.futureRemove = [ ]
    app.stockGraphList = [ ]
    app.stockGraph = 0
    app.probCirclesList = []
    app.circleX = 0
    app.circleY = 0
    app.percentChangeList = []
    app.probabilityList = []
    app.lengthRSI = 20
    app.xAxisRSI = []
    app.yAxisRSI = []
    app.probCirclesListRSI = []
    app.circleXRSI = ''
    app.circleYRSI = 0
    app.secondGraph = True
    app.probCirclesListSMA = []
    app.xAxisSMA = []
    app.yAxisSMA = []
    app.circleXSMA = ''
    app.circleYSMA = 0
    app.suggestion = ''
    app.lowerProfit = 0
    app.upperProfit = 0

    app.tickerHistList = []
    app.histStocksBought = []
    app.histRemove = []
    app.histDates = []
    app.histGraphList = []
    app.histXAxis = []
    app.histYAxis = []
    app.histCircleX = ''
    app.histCircleY = 0
    app.histCirclesList = []
    app.histCirclesListStock = []
    app.histXAxisStock = []
    app.histYAxisStock = []
    app.histCircleXStock = ''
    app.histCircleYStock = 0
    app.realHistYAxis = []
    app.histLength = 1
    app.histLengthStock = 1 

    #https://www.vecteezy.com/vector-art/1951380-business-graph-chart-of-stock-market-investment-on-blue-background
    app.titleBackgroundImage = app.loadImage("StocksBackground.png")
    app.titleBackgroundImage = app.scaleImage(app.titleBackgroundImage, 3)
    
    #https://www.shutterstock.com/search/stock+chart+white
    app.modelsBackgroundImage = app.loadImage("ModelsBackground.png")
    app.modelsBackgroundImage = app.scaleImage(app.modelsBackgroundImage, 1.85)

    #https://en.wikipedia.org/wiki/File:Back_Arrow.svg
    app.arrowImage = app.loadImage("BackArrow.png")
    app.arrowImage = app.scaleImage(app.arrowImage, .025)

###########################################################################################################################################################################
#                                   REGULAR HELPER FUNCTIONS
###########################################################################################################################################################################

#rounds to 2 decimals
#https://stackoverflow.com/questions/13463556/round-an-answer-to-2-decimal-places-in-python
def round_decimal2(x):
    return Decimal(x).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

#rounds to 1 decimal
#https://stackoverflow.com/questions/13463556/round-an-answer-to-2-decimal-places-in-python
def round_decimal1(x):
    return Decimal(x).quantize(Decimal(".1"), rounding=ROUND_HALF_UP)

#rounds up when needed
#https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    # You do not need to understand how this function works.
    import decimal
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#calculates the midpoint given four points
def midPoint(x1, x2, y1, y2):
    x3 = (x1 + x2) // 2
    y3 = (y1 + y2) // 2
    return x3, y3

#calculates distance between two points
def distance(x1, y1, x2, y2):
    return ((float(x2)-float(x1))**2 + (float(y2)-float(y1))**2)**.5

###########################################################################################################################################################################
#                                   TITLE PAGE
###########################################################################################################################################################################

def titlePage_mousePressed(app, event):
    #checks to see if user clicks historical simulator button
    if (event.x > 50 and event.x < 650 and 
        event.y > 310 + 40 and event.y < 310 + 40 + 75):
        app.mode = 'historicalSimulatorMode'
    
    #checks to see if user clicks on future predictions button
    if (event.x > 50 and event.x < 650 and 
        event.y > 440 + 40 and event.y < 440 + 40 + 75):
        app.mode = 'futurePredictionsMode'

def titlePage_redrawAll(app, canvas):
    #creates background image
    canvas.create_image(350, 375, image=ImageTk.PhotoImage(app.titleBackgroundImage))

    #creates the view stocks button
    canvas.create_text(350, 125, text = app.title, 
                        font = f'Gautami 65 bold', fill = "white")
    #creates the historical simulator button
    canvas.create_rectangle(50, 310 + 40, 50 + 2 * 300, 
                            310 + 40 + 75, fill = "green")
    txtX1, txtY1 = midPoint(50, 50 + 2 * 300, 310 + 40, 
                            310 + 40 + 75)
    canvas.create_text(txtX1, txtY1, text = "Historical Simulator", 
                        font = f'Gautami 35 bold', fill = "white")
    #creates the future predicitions button
    canvas.create_rectangle(50, 440 + 40, 50 + 2 * 300, 
                            440 + 40 + 75, fill = "green")
    txtX1, txtY1 = midPoint(50, 50 + 2 * 300, 440 + 40, 
                            440 + 40 + 75)
    canvas.create_text(txtX1, txtY1, text = "Future Predictions", 
                        font = f'Gautami 35 bold', fill = "white")

###########################################################################################################################################################################
#                                   HISTORICAL SIMULATOR MODE
###########################################################################################################################################################################

#checks to see if the date entered is in proper format
def isDateLegal(dateBought):
    dateBought = dateBought.strip()
    if (len(dateBought) != 10 or not dateBought[:3].isnumeric() or dateBought[4] != '-' or
        not dateBought[5:7].isnumeric() or dateBought[7] != '-' or 
        not dateBought[8:].isnumeric() or int(dateBought[:3]) > 2021 or 
        int(dateBought[5:7]) < 1 or int(dateBought[5:7]) > 12 or 
        int(dateBought[8:]) < 1 or int(dateBought[8:]) > 31):
        return False
    else: 
        return True
    
#checks to see if the date entered exists in the current dataframe
def isDateAcceptable(dateBought, ticker):
    try:
        history = getStockHist(ticker, "max")
        potential = history.loc[dateBought]
        return True
    except:
        return False

#checks to see if mouse pressed in the historical simulator mode
def historicalSimulatorMode_mousePressed(app, event):
    if distance(event.x, event.y, 25, 25) <= 15:
        app.mode = "titlePage"
    
    #checks to see if add stock button clicked
    if (event.x > 50 and event.x < 225 
        and event.y > 575 and event.y < 650):
        if len(app.tickerHistList) == 7:
            app.showMessage('You can only have a maximum of 7 stocks in your portfolio')
        else:
            #asks user to enter a ticker symbol
            ticker = app.getUserInput("What stock do you want to buy? (Enter ticker symbol)")
            #does not bring up error if user cancels
            if ticker == None:
                pass
            elif ticker.upper() in app.tickerHistList:
                app.showMessage("This ticker is already in your portfolio")
            else:
                #checks for valid ticker entered
                while not isTickerLegal(ticker):
                    ticker = app.getUserInput("You entered an invalid symbol. Try again.")
                    if ticker == None:
                        break
                    elif ticker.upper() in app.tickerHistList:
                        app.showMessage("This ticker is already in your portfolio")
                        ticker = None
                        break
                if ticker != None:
                    #asks user for number of shares to buy
                    stocksBought = app.getUserInput("How many shares do you want to buy?")
                    #does not bring up error if user cancels
                    if stocksBought == None:
                        pass
                    else:
                        #checks to see if valid input entered
                        while(not isSharesLegal(stocksBought)):
                            stocksBought = app.getUserInput("You entered an invalid input. Try again.")
                            if stocksBought == None:
                                break
                    if stocksBought != None:
                        #asks for the date of investment
                        dateBought = app.getUserInput("What date did you want to buy them? (YYYY-MM-DD)")
                        #does not bring up error if user cancels
                        if dateBought == None:
                            pass
                        else:
                            #checks to see if date format is correct
                            while(not isDateLegal(dateBought)):
                                dateBought = app.getUserInput("You entered an invalid input. Try again. (YYYY-MM-DD)")
                                if dateBought == None:
                                    break
                            #checks to see if date exists
                            while(not isDateAcceptable(dateBought, ticker)):
                                dateBought = app.getUserInput("The market was not open this day. Try again. (YYYY-MM-DD)")
                                if dateBought == None:
                                    break
                        #if date exists then we modify model
                        if dateBought != None:
                            app.tickerHistList.append(ticker.upper())
                            app.histStocksBought.append(stocksBought)
                            app.histRemove.append(len(app.futureRemove)+1)
                            app.histDates.append(dateBought)
    
    #checks to see if remove button was clicked for any of the stocks
    for x in range(len(app.histRemove)):
        if(event.x > 75 + 4 * 125 and event.x < 140 + 4 * 125  and 
            event.y >  112 + 40 * (x+1) and event.y < 137 + 40 * (x+1)):
            app.tickerHistList.pop(x)
            app.histRemove.pop(x)
            app.histDates.pop(x)
            app.histStocksBought.pop(x)
    
    #checks to see if view models button is pressed
    if (event.x > 475 and event.x < 650 and 
        event.y > 575 and event.y < 650):
        if len(app.tickerHistList) == 0:
            app.showMessage('You must create a protfolio before viewing models')
        else:
            histSetUp(app)
            createSimulatorGraph(app)
            createFirstGraph(app)
            createSecondGraph(app)
            app.mode = "historicalSimulatorModelMode"

#draws the stock profile
def drawStockOnHistoricProfile(app, canvas):
    #loops through all the tickers in the tickerHistList
    #draws the ticker, shares, date, histPrice, marktValue and remove button
    for x in range(len(app.tickerHistList)):
        ticker = app.tickerHistList[x]
        shares = str(app.histStocksBought[x])
        date = str(app.histDates[x])
        histPrice = str(getHistPrice(ticker, date))
        marketValue = str(round_decimal2(int(shares) * float(histPrice)))
        canvas.create_text(50, 125 + 40 * (x+1), text = ticker, 
                            font = f'Gautami 15 bold', anchor="w")
        canvas.create_text(50 + 75, 125 + 40 * (x+1), text = shares, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_text(60 + 2 * 75, 125 + 40 * (x+1), text = date, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_text(60 + 275, 125 + 40 * (x+1), text = histPrice, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_text(60 + 375, 125 + 40 * (x+1), text = marketValue, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_rectangle(75 + 4 * 125, 112 + 40 * (x+1), 140 + 4 * 125, 137 + 40 * (x+1), 
                                fill = "red")
        txtX1, txtY1 = midPoint(75 + 4 * 125, 140 + 4 * 125, 112 + 40 * (x+1), 137 + 40 * (x+1))
        canvas.create_text(txtX1, txtY1, text = "Remove", 
                        font = f'Gautami 13 bold', fill = "white")

#draws on the historicalSimulatorMode
def historicalSimulatorMode_redrawAll(app, canvas):
    #creates the background image
    canvas.create_image(25, 25, image=ImageTk.PhotoImage(app.arrowImage))
    
    #creates inital portfolio and all its variables
    canvas.create_text(app.width/2, 75, text = "Create your portfolio", 
                        font = f'Gautami 45 bold')
    canvas.create_text(50, 125, text = "Stock", 
                        font = f'Gautami 15 bold', anchor="w")
    canvas.create_text(50 + 75, 125, text = "Shares", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_text(60 + 75 * 2, 125, text = "Date Bought", 
                        font = f'Gautami 15 bold', anchor = 'w')
    canvas.create_text(60 + 275, 125, text = "Avg Cost", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_text(60 + 375, 125, text = "Market Value", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_text(50 + 525, 125, text = "Remove", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_line(30, 140, 655, 140, width = 5)
    canvas.create_rectangle(50, 575, 225, 650, 
                            fill = "green")
    txtX1, txtY1 = midPoint(50, 225, 575, 650)
    canvas.create_text(txtX1, txtY1, text = "Add Stock", 
                        font = f'Gautami 25 bold', fill = "white")
    canvas.create_rectangle(475, 575, 650, 650, 
                            fill = "green")
    txtX1, txtY1 = midPoint(475, 650, 575, 650)
    canvas.create_text(txtX1, txtY1, text = "View Models", 
                        font = f'Gautami 25 bold', fill = "white")
    drawStockOnHistoricProfile(app, canvas)

##################################################################################################################################################################
#                               HISTORICAL SIMULATOR MODEL MODE
##################################################################################################################################################################

#class for all stocks in the history mode
class histStocks(object):
    def __init__(self, ticker, date, stocksBought):
        self.ticker = ticker
        self.startDate = date
        self.shares = stocksBought
    
    #gets the ticker symbol of stock object
    def getTicker(self):
        return self.ticker
    
    #gets shares of stock object
    def getShares(self):
        return self.shares
    
    #gets the history as a datafram from stock object
    def getHist(self, periodLength):
        stock = yf.Ticker(self.ticker)
        history = stock.history(period = periodLength)
        return history
    
    #creates a list of specified length of dates and prices from dataframe
    def getDates(self, length):
        history = self.getHist("max")
        listOfAllDates = []
        listOfNeededDates = []
        listOfAllCloses = []
        listOfNeededCloses = []
        newListOfNeededDates = [ ]
        newListOfNeededCloses = [ ]
        for ind in history.index:
            # partially from https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
            newDate = ind.to_pydatetime().strftime("%Y-%m-%d")
            listOfAllDates.append(newDate)
            listOfAllCloses.append(history.loc[ind, "Close"])
        indexOfStartDate = listOfAllDates.index(self.startDate)
        for i in range(indexOfStartDate, len(listOfAllDates)):
            listOfNeededDates.append(listOfAllDates[i])
            listOfNeededCloses.append(listOfAllCloses[i])
        if length == 1 or len(listOfNeededDates)-1-length <= 0:
            return listOfNeededDates, listOfNeededCloses
        else:
            for i in range(len(listOfNeededDates)-1,len(listOfNeededDates)-1-length, -1):
                newListOfNeededDates.insert(0, listOfNeededDates[i])
                newListOfNeededCloses.insert(0, listOfNeededCloses[i])
            return newListOfNeededDates, newListOfNeededCloses

#makes every ticker entered an object of the class
def histSetUp(app):
    list = []
    for i in range(len(app.tickerHistList)):
        stock = histStocks(app.tickerHistList[i], app.histDates[i], app.histStocksBought[i])
        list.append(stock)
    app.histGraphList = copy.copy(list)
    app.histStockGraph = app.histGraphList[0]

#creates the x and y coordinates of the points for each stock
def createSecondGraph(app):
    app.histCirclesListStock = []
    xAxisStock, yAxisStock = app.histStockGraph.getDates(app.histLengthStock)
    ind = app.histGraphList.index(app.histStockGraph)
    shares = app.histStocksBought[ind]
    newYAxisStock = []
    for x in yAxisStock:
        newYAxisStock.append(float(shares) * x)

    yCoords = []
    unitYSpace = 175 / (max(newYAxisStock) - (min(newYAxisStock)))
    for coor in newYAxisStock:
        y1 = 600
        y1 -= (coor-min(newYAxisStock)) * unitYSpace
        yCoords.append(y1)
    
    xCoords = []
    unitXSpace = 350 / (len(xAxisStock) - 1)
    for i in range(len(yCoords)):
        x1 = 50
        x1 += i * unitXSpace
        xCoords.append(x1)

    app.histXAxisStock = xAxisStock
    app.histYAxisStock = newYAxisStock
    
    for ind in range(len(xCoords)):
        point = ProbCircles(cx=xCoords[ind], cy=yCoords[ind], r=5)
        app.histCirclesListStock.append(point)

#sorts all the lists of Dates and Closes
def createSimulatorGraph(app):
    allXAxis = []
    allYAxis = []
    sortedXAxis = []
    sortedYAxis = []
    for stock in app.histGraphList:
        xAxis, yAxis = stock.getDates(app.histLength)
        allXAxis.append(xAxis)
        shares = stock.getShares()
        newYAxis = []
        for x in yAxis:
            newYAxis.append(float(shares)*x)
        allYAxis.append(newYAxis)
    for i in range(len(allXAxis)):
        if len(sortedXAxis) == 0:
            sortedXAxis.append(allXAxis[i])
            sortedYAxis.append(allYAxis[i])
        else:
            x = 0
            while(len(allXAxis[i]) > len(sortedXAxis[x])):
                x+=1
                if x >= len(sortedXAxis):
                    break
            sortedXAxis.insert(x, allXAxis[i])
            sortedYAxis.insert(x, allYAxis[i])
    app.histXAxis = sortedXAxis
    app.histYAxis = sortedYAxis

#creates the x and y coordinates of the points for the overall portfolio
def createFirstGraph(app):
    app.histCirclesList = []
    total = 0
    for x in app.histYAxis:
        total+=max(x)
    yValues = []
    for x in range(len(app.histXAxis[-1])):
        y1 = 0
        for y in range(len(app.histXAxis)):
            if app.histXAxis[-1][x] in app.histXAxis[y]:
                y1+=app.histYAxis[y][app.histXAxis[y].index(app.histXAxis[-1][x])]
        yValues.append(y1)
    
    app.realHistYAxis = yValues
    mini = min(app.realHistYAxis)
    
    yCoords = []
    unitYSpace = 175 / (total-mini)
    for coor in yValues:
        y1 = 225
        y1 -= (coor-mini) * unitYSpace
        yCoords.append(y1)
    
    xCoords = []
    unitXSpace = 350 / (len(app.histXAxis[-1]) - 1)
    for i in range(len(yCoords)):
        x1 = 50
        x1 += i * unitXSpace
        xCoords.append(x1)

    for ind in range(len(xCoords)):
        point = ProbCircles(cx=xCoords[ind], cy=yCoords[ind], r=5)
        app.histCirclesList.append(point)

def historicalSimulatorModelMode_mousePressed(app, event):
    #checks to see if back arrow is pressed
    if distance(event.x, event.y, 25, 25) <= 15:
        app.mode = "historicalSimulatorMode"

    #checks to see if any of the stock buttons were pressed
    for y in range(len(app.histGraphList)):
        space = 85
        if (event.x > 50+ y * space and event.x < 125+ y * space 
            and event.y > 345 and event.y < 375):
            app.histStockGraph = app.histGraphList[y]
            createSecondGraph(app)
    
    #checks to see if length is changed for second graph
    if (event.x > 50 and event.x < 125 and 
        event.y > 660 and event.y < 690):
        app.histLengthStock = 1
        createSecondGraph(app)
    elif (event.x > 135 and event.x < 210 and 
        event.y > 660 and event.y < 690):
        app.histLengthStock = 240
        createSecondGraph(app)
    elif (event.x > 220 and event.x < 295 and 
        event.y > 660 and event.y < 690):
        app.histLengthStock = 60
        createSecondGraph(app)
    elif (event.x > 305 and event.x < 380 and 
        event.y > 660 and event.y < 690):
        app.histLengthStock = 20
        createSecondGraph(app)
    elif (event.x > 390 and event.x < 465 and 
        event.y > 660 and event.y < 690):
        app.histLengthStock = 5
        createSecondGraph(app)
    
    #checks to see if length is changed for first graph
    if (event.x > 50 and event.x < 125 and 
        event.y > 285 and event.y < 315):
        app.histLength = 1
        createSimulatorGraph(app)
        createFirstGraph(app)
    elif (event.x > 135 and event.x < 210 and 
        event.y > 285 and event.y < 315):
        app.histLength = 240
        createSimulatorGraph(app)
        createFirstGraph(app)
    elif (event.x > 220 and event.x < 295 and 
        event.y > 285 and event.y < 315):
        app.histLength = 60
        createSimulatorGraph(app)
        createFirstGraph(app)
    elif (event.x > 305 and event.x < 380 and 
        event.y > 285 and event.y < 315):
        app.histLength = 20
        createSimulatorGraph(app)
        createFirstGraph(app)
    elif (event.x > 390 and event.x < 465 and 
        event.y > 285 and event.y < 315):
        app.histLength = 5
        createSimulatorGraph(app)
        createFirstGraph(app)

def historicalSimulatorModelMode_mouseMoved(app, event):
    #checks to see if mouse if currently over a point on the first graph
    for ind in range(len(app.histCirclesList)):
        circle = app.histCirclesList[ind]
        if distance(event.x, event.y, circle.cx, circle.cy) <= circle.r:
            app.histCircleX = app.histXAxis[-1][ind]
            y1 = 0
            for y in range(len(app.histXAxis)):
                if app.histXAxis[-1][ind] in app.histXAxis[y]:
                    y1+=app.histYAxis[y][app.histXAxis[y].index(app.histXAxis[-1][ind])]
            app.histCircleY = y1
            break
    
    #checks to see if mouse if currently over a point on the first graph
    for ind in range(len(app.histCirclesListStock)):
        circle = app.histCirclesListStock[ind]
        if distance(event.x, event.y, circle.cx, circle.cy) <= circle.r:
            app.histCircleXStock = app.histXAxisStock[ind]
            app.histCircleYStock = app.histYAxisStock[ind]
            break

def historicalSimulatorModelMode_redrawAll(app, canvas):
    #creates the outline for the first graph
    canvas.create_image(350, 375, image=ImageTk.PhotoImage(app.modelsBackgroundImage))
    canvas.create_image(25, 25, image=ImageTk.PhotoImage(app.arrowImage))
    canvas.create_rectangle(50, 50, 400, 225)
    canvas.create_text(225, 270, text = "Date", font = 'Guatami 10')
    canvas.create_text(10, 137.5, text = "Portfolio Value", font = 'Guatami 10', angle = 90)
    canvas.create_text(225, 25, text = "Portfolio Value Overtime", font = 'Guatami 20')
    
    #creates xAxis of the first graph
    xAxis = app.histXAxis[-1]
    unitXSpace = 350 / 4
    lengthOfXAxis = len(xAxis)
    textX = [ xAxis[0], xAxis[(lengthOfXAxis-1)//4], xAxis[(lengthOfXAxis-1)//2], xAxis[((lengthOfXAxis-1)//2)+((lengthOfXAxis-1)//4)], xAxis[lengthOfXAxis-1] ]
    y = 0
    for x in range(5):
        x1 = 50
        x1 += unitXSpace * x
        canvas.create_line(x1, 220, x1, 230, width = 3)
        canvas.create_text(x1 + 5, 235, text = str(textX[y]), 
                            font = f'Gautami 7', angle = 45, anchor = "e")
        y += 1
    
    #creates the yAxis for the first graph
    total = 0
    for x in app.histYAxis:
        total+=max(x)
    unitYSpace = 175 / 4
    mini = min(app.realHistYAxis)
    mid = ((total+ + mini)/ 2)
    textY = [ roundHalfUp(mini), roundHalfUp((mid + mini)/ 2), roundHalfUp(mid), roundHalfUp((mid + total)/ 2), roundHalfUp(total) ]
    x = -1
    for y in range(5):
        y1 =  50
        y1 += unitYSpace * y
        canvas.create_line(45, y1, 55, y1, width = 3)
        canvas.create_text(33, y1, text = str(textY[x]), 
                            font = f'Gautami 7')
        x-=1
    
    #plots the points on the graph
    length = len(app.histCirclesList) // 30
    if length < 1:
        length = 1
    for ind in range(0, len(app.histCirclesList), length):
            circle = app.histCirclesList[ind]
            canvas.create_oval(circle.cx-circle.r, circle.cy-circle.r, 
                                circle.cx+circle.r, circle.cy+circle.r, 
                                fill = "black")
    
    #draws outline of the first box
    canvas.create_rectangle(450, 50, 650, 125)
    canvas.create_text(460, 70, text = f'Date: {app.histCircleX}', anchor = 'w', font = f'Gautami 10')
    canvas.create_text(460, 105, text = f'Portfolio Value: ${round_decimal2(app.histCircleY)}', 
                                        anchor = 'w', font = f'Gautami 10')
    
    #calculates all the values needed for second box on side
    currValue = 0
    for x in app.histYAxis:
        currValue+=x[-1]

    startValue = 0
    for x in app.histYAxis:
        startValue+=x[0]

    profit = currValue - startValue
    percentChange = (profit / startValue) * 100
    
    #creates the second box on the side
    canvas.create_rectangle(450, 150, 650, 225)
    canvas.create_text(460, 160, text = f'Final Portfolio Value: ${round_decimal2(currValue)}', anchor = 'w', font = f'Gautami 10')
    canvas.create_text(460, 160+27.5, text = f'Profit: {round_decimal2(profit)} dollars', 
                                        anchor = 'w', font = f'Gautami 10')
    canvas.create_text(460, 215, text = f'Percent Change: {round_decimal2(percentChange)}%', 
                                        anchor = 'w', font = f'Gautami 10')
    
    #draws all the length buttons for the first graph
    canvas.create_rectangle(50, 285, 125, 315, fill = "green")
    canvas.create_text(87.5, 300, text = "max", fill = "white")
    canvas.create_rectangle(135, 285, 210, 315, fill = "green")
    canvas.create_text(172.5, 300, text = "1 year", fill = "white")
    canvas.create_rectangle(220, 285, 295, 315, fill = "green")
    canvas.create_text(257.5, 300, text = "3 months", fill = "white")
    canvas.create_rectangle(305, 285, 380, 315, fill = "green")
    canvas.create_text(342.5, 300, text = "1 month", fill = "white")
    canvas.create_rectangle(390, 285, 465, 315, fill = "green")
    canvas.create_text(427.5, 300, text = "1 week", fill = "white")

    #creates the third box on the side
    canvas.create_rectangle(50, 425, 400, 600)
    canvas.create_text(225, 645, text = "Date", font = 'Guatami 10')
    canvas.create_text(10, 512.5, text = "Market Value of Stock", font = 'Guatami 10', angle = 90)
    canvas.create_text(225, 400, text = f'Market Value of {app.histStockGraph.getTicker()} Overtime', font = 'Guatami 20')

    #creates the xAxis for the second graph
    unitXSpace = 350 / 4
    lengthOfXAxis = len(app.histXAxisStock)
    textX = [ app.histXAxisStock[0], app.histXAxisStock[(lengthOfXAxis-1)//4], app.histXAxisStock[(lengthOfXAxis-1)//2], app.histXAxisStock[((lengthOfXAxis-1)//2)+((lengthOfXAxis-1)//4)], app.histXAxisStock[lengthOfXAxis-1] ]
    y = 0
    for x in range(5):
        x1 = 50
        x1 += unitXSpace * x
        canvas.create_line(x1, 595, x1, 605, width = 3)
        canvas.create_text(x1 + 5, 610, text = str(textX[y]), 
                            font = f'Gautami 7', angle = 45, anchor = "e")
        y += 1
    
    #creates the yAxis for the second graph
    unitYSpace = 175 / 4
    mid = (max(app.histYAxisStock) + min(app.histYAxisStock)) / 2
    textY = [ roundHalfUp(min(app.histYAxisStock)), roundHalfUp((mid + min(app.histYAxisStock))/ 2), roundHalfUp(mid), roundHalfUp((mid + max(app.histYAxisStock))/ 2), roundHalfUp(max(app.histYAxisStock)) ]
    x = -1
    for y in range(5):
        y1 =  425
        y1 += unitYSpace * y
        canvas.create_line(45, y1, 55, y1, width = 3)
        canvas.create_text(33, y1, text = str(textY[x]), 
                            font = f'Gautami 7')
        x-=1

    #plots all the points on the second graph
    lengthStock = len(app.histCirclesListStock) // 30
    if lengthStock < 1:
        lengthStock = 1
    for ind in range(0, len(app.histCirclesListStock), lengthStock):
        circle = app.histCirclesListStock[ind]
        canvas.create_oval(circle.cx-circle.r, circle.cy-circle.r, 
                            circle.cx+circle.r, circle.cy+circle.r, 
                            fill = "red")
    
    #creates the third box on the side
    canvas.create_rectangle(450, 425, 650, 500)
    canvas.create_text(460, 445, text = f'Date: {app.histCircleXStock}', anchor = "w", font = 'Guatami 10')
    canvas.create_text(460, 480, text = f'Market Value: ${round_decimal2(app.histCircleYStock)}', anchor = "w", font = 'Guatami 10')

    #calculates values needed for fourth box
    currValueStock = app.histYAxisStock[-1]

    startValueStock = app.histYAxisStock[0]

    profitStock = currValueStock - startValueStock
    percentChangeStock = (profitStock / startValueStock) * 100
    
    #creates fourth box on the side
    canvas.create_rectangle(450, 525, 650, 600)
    canvas.create_text(460, 535, text = f'Final Market Value: ${round_decimal2(currValueStock)}', anchor = 'w', font = f'Gautami 10')
    canvas.create_text(460, 535+27.5, text = f'Profit: {round_decimal2(profitStock)} dollars', 
                                        anchor = 'w', font = f'Gautami 10')
    canvas.create_text(460, 590, text = f'Percent Change: {round_decimal2(percentChangeStock)}%', 
                                        anchor = 'w', font = f'Gautami 10')
    
    #draws all the stock buttons
    y = 0
    for x in app.histGraphList:
        space = 85
        canvas.create_rectangle(50+ y * space, 345, 125+ y * space, 375, fill = "red")
        midX, midY = midPoint(50+ y * space, 125+ y * space, 345, 375)
        canvas.create_text(midX, midY, text = str(x.getTicker()), fill = "white")
        y += 1 
    
    #draws the length buttons for the second graph
    canvas.create_rectangle(50, 660, 125, 690, fill = "green")
    canvas.create_text(87.5, 675, text = "max", fill = "white")
    canvas.create_rectangle(135, 660, 210, 690, fill = "green")
    canvas.create_text(172.5, 675, text = "1 year", fill = "white")
    canvas.create_rectangle(220, 660, 295, 690, fill = "green")
    canvas.create_text(257.5, 675, text = "3 months", fill = "white")
    canvas.create_rectangle(305, 660, 380, 690, fill = "green")
    canvas.create_text(342.5, 675, text = "1 month", fill = "white")
    canvas.create_rectangle(390, 660, 465, 690, fill = "green")
    canvas.create_text(427.5, 675, text = "1 week", fill = "white")
    



###########################################################################################################################################################################
#                                   PROJECT SPECIFIC HELPER FUNCTIONS
###########################################################################################################################################################################

#gets the close price when given a ticker and date
def getHistPrice(ticker, date):
    history = getStockHist(ticker, "max")
    return round_decimal2(history.loc[date, "Close"])

#gets the price of the stock for the most recent day
def getTodayPrice(ticker):
    price = 0
    tickerHist = getStockHist(ticker, "1d")
    for ind in tickerHist.index:
        price = tickerHist.loc[ind, "Close"]
    return round_decimal2(price)

#gets the dataframe showing the histroy of a stock
def getStockHist(ticker, length):
    ticker = ticker.upper()
    stock = yf.Ticker(ticker)
    return stock.history(period = length)

#checks to see if the shares entered are legal
def isSharesLegal(stocksBought):
    if not stocksBought.isdigit() or int(stocksBought) <= 0:
        return False
    else:
        return True

#checks to see if the ticker entered is legal
def isTickerLegal(ticker):
    tickerHist = getStockHist(ticker, "5d")
    listOfOpenPrices = [ ]
    for ind in tickerHist.index:
        listOfOpenPrices.append(tickerHist.loc[ind, "Open"])
    if len(listOfOpenPrices) == 0:
        return False
    else:
        return True

###########################################################################################################################################################################
#                                   FUTURE PREDICTIONS MODE
###########################################################################################################################################################################

#checks to see if mouse is pressed on futurePredicitionsMode
def futurePredictionsMode_mousePressed(app, event):
    if distance(event.x, event.y, 25, 25) <= 15:
        app.mode = "titlePage"
    
    #checks to see if add stock is pressed
    if (event.x > 50 and event.x < 225 
        and event.y > 575 and event.y < 650):
        if len(app.tickerFutureList) == 7:
            app.showMessage('You can only have a maximum of 7 stocks in your portfolio')
        else:
            #asks user to input a ticker
            ticker = app.getUserInput("What stock do you want to buy? (Enter ticker symbol)")
            #allows user to cancel without an error
            if ticker == None:
                pass
            elif ticker.upper() in app.tickerFutureList:
                app.showMessage("This ticker is already in your portfolio")
            else:
                #checks to see if ticker is legal
                while not isTickerLegal(ticker):
                    ticker = app.getUserInput("You entered an invalid symbol. Try again.")
                    if ticker == None:
                        break
                    elif ticker.upper() in app.tickerFutureList:
                        app.showMessage("This ticker is already in your portfolio")
                        ticker = None
                        break
                if ticker != None:
                    #asks user for the number of shares they want to buy
                    stocksBought = app.getUserInput("How many shares do you want to buy?")
                    #allows user to cancel without an error
                    if stocksBought == None:
                        pass
                    else:
                        #checks to see if the shares are valid
                        while(not isSharesLegal(stocksBought)):
                            stocksBought = app.getUserInput("You entered an invalid input. Try again.")
                            if stocksBought == None:
                                break
                    #modifies moel if everything is valid
                    if stocksBought != None:
                        app.tickerFutureList.append(ticker.upper())
                        app.futureStocksBought.append(stocksBought)
                        app.futureRemove.append(len(app.futureRemove)+1)
    
    #if remove is pressed on any stocks then we remove the stock
    for x in range(len(app.futureRemove)):
        if(event.x > 75 + 4 * 125 and event.x < 140 + 4 * 125  and 
            event.y >  112 + 40 * (x+1) and event.y < 137 + 40 * (x+1)):
            app.tickerFutureList.pop(x)
            app.futureRemove.pop(x)
            app.futureStocksBought.pop(x)

    #checks to see if view models button is pressed
    if (event.x > 475 and event.x < 650 and 
        event.y > 575 and event.y < 650):
        if len(app.tickerFutureList) == 0:
            app.showMessage('You must create a protfolio before viewing models')
        else:
            createFutureProbabilityModel(app)
            createIndicatorGraph(app)
            suggestion(app)
            getSecondBox(app)
            app.mode = "futurePredictionsModelMode"

def drawStockOnFutureProfile(app, canvas):
    #draws each stock and its info on the portfolio page
    for x in range(len(app.tickerFutureList)):
        ticker = app.tickerFutureList[x]
        shares = str(app.futureStocksBought[x])
        avgPrice = str(getTodayPrice(ticker))
        marketValue = str(round_decimal2(int(shares) * float(avgPrice)))
        canvas.create_text(50, 125 + 40 * (x+1), text = ticker, 
                            font = f'Gautami 15 bold', anchor="w")
        canvas.create_text(50 + 125, 125 + 40 * (x+1), text = shares, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_text(50 + 2 * 125, 125 + 40 * (x+1), text = avgPrice, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_text(50 + 3 * 125, 125 + 40 * (x+1), text = marketValue, 
                            font = f'Gautami 15 bold', anchor = "w")
        canvas.create_rectangle(75 + 4 * 125, 112 + 40 * (x+1), 140 + 4 * 125, 137 + 40 * (x+1), 
                                fill = "red")
        txtX1, txtY1 = midPoint(75 + 4 * 125, 140 + 4 * 125, 112 + 40 * (x+1), 137 + 40 * (x+1))
        canvas.create_text(txtX1, txtY1, text = "Remove", 
                        font = f'Gautami 13 bold', fill = "white")

def futurePredictionsMode_redrawAll(app, canvas):
    #creates the background image
    canvas.create_image(25, 25, image=ImageTk.PhotoImage(app.arrowImage))
    
    #draws outline of portfolio
    canvas.create_text(app.width/2, 75, text = "Create your portfolio", 
                        font = f'Gautami 45 bold')
    canvas.create_text(50, 125, text = "Stock", 
                        font = f'Gautami 15 bold', anchor="w")
    canvas.create_text(50 + 125, 125, text = "Shares", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_text(50 + 2 * 125, 125, text = "Avg Cost", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_text(50 + 3 * 125, 125, text = "Market Value", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_text(75 + 4 * 125, 125, text = "Remove", 
                        font = f'Gautami 15 bold', anchor = "w")
    canvas.create_line(30, 140, 655, 140, width = 5)
    canvas.create_rectangle(50, 575, 225, 650, 
                            fill = "green")
    txtX1, txtY1 = midPoint(50, 225, 575, 650)
    canvas.create_text(txtX1, txtY1, text = "Add Stock", 
                        font = f'Gautami 25 bold', fill = "white")
    canvas.create_rectangle(475, 575, 650, 650, 
                            fill = "green")
    txtX1, txtY1 = midPoint(475, 650, 575, 650)
    canvas.create_text(txtX1, txtY1, text = "View Models", 
                        font = f'Gautami 25 bold', fill = "white")
    drawStockOnFutureProfile(app, canvas)

###########################################################################################################################################################################
#                                   FUTURE PREDICTIONS MODEL MODE
###########################################################################################################################################################################

#create a class to find all properties of the stocks on the graph
class graphStocks(object):
    def __init__(self, x, stocks):
        self.ticker = x.upper()
        self.shares = stocks

    #returns the ticker symbol
    def getTicker(self):
        return self.ticker
    
    def getShares(self):
        return self.shares

    #returns the histroy of a given stock as a dataframe
    def getHist(self, periodLength):
        stock = yf.Ticker(self.ticker)
        history = stock.history(period = periodLength)
        return history

    #returns the prices from the past year for a stock
    def getPastYearPrices(self, periodLength):
        history = self.getHist(periodLength)
        pastYearPrices = [ ] 
        for i in history.index:
            pastYearPrices.append(history.loc[i, "Close"])
        return pastYearPrices
    
    #returns the percent change for each day
    def getPercentChangeList(self):
        pastYearPrices = self.getPastYearPrices("1y")
        percentChangeList = [ ]
        for x in range(len(pastYearPrices)-1, 0, -1):
            percentChangeList.append((pastYearPrices[x]-pastYearPrices[x-1])*100 / pastYearPrices[x-1])
        percentChangeList = sorted(percentChangeList)
        return percentChangeList

    #calculates the probabiltity that the stock changes 
    def getProbabilityList(self):
        percentChangeList = self.getPercentChangeList()
        probabilityList = [ ]
        for x in range(len(percentChangeList)):
            probabilityList.append((x+1)/len(percentChangeList))
        return probabilityList
    
    #calculates the RSI when given a specified length of time
    def getRSI(self, length):
        pastPrices = self.getPastYearPrices("max")
        down = []
        up = []
        listRSI = []
        listDates = []
        dayCount = 1
        while len(listRSI) < length:
            if len(pastPrices) - dayCount - 14 < 0:
                break
            for i in range(len(pastPrices) - dayCount, len(pastPrices) - dayCount - 14, -1):
                currDiff = pastPrices[i] - pastPrices[i-1]
                if currDiff < 0:
                    down.append(abs(currDiff))
                else:
                    up.append(currDiff)
            
            rsi = 100 - (100 / (1 + (sum(up)/14) / (sum(down)/14)))
            listRSI.insert(0, rsi)
            dayCount += 1
        stockHistory = self.getHist("max")
        x = 0
        while len(listDates) < len(listRSI):
            # partially from https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
            listDates.insert(0, stockHistory.index[-1-x].to_pydatetime().strftime("%Y-%m-%d"))
            x+=1
        return listDates, listRSI
    
    #calculates the SMA given a specified length of time
    def getSMA(self, length):
        pastPrices = self.getPastYearPrices("max")
        listSMA = []
        listDates = []
        dayCount = 1
        while len(listSMA) < length:
            past5Days = []
            if len(pastPrices) - dayCount - 5 < 0:
                break
            for i in range(len(pastPrices) - dayCount, len(pastPrices) - dayCount - 5, -1):
                past5Days.append(pastPrices[i])
            
            sma = (sum(past5Days)/5)
            listSMA.insert(0, sma)
            dayCount += 1
        stockHistory = self.getHist("max")
        x = 0
        while len(listDates) < len(listSMA):
            # partially from https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
            listDates.insert(0, stockHistory.index[-1-x].to_pydatetime().strftime("%Y-%m-%d"))
            x+=1
        return listDates, listSMA

def futurePredictionsModelMode_mousePressed(app, event):
    #checks to see if back arrow was pressed
    if distance(event.x, event.y, 25, 25) <= 15:
        app.mode = "futurePredictionsMode"
    
    #checks to see if RSI or SMA buttons are pressed
    if (event.x >= 325 and event.x <= 400 and
        event.y >=375 and event.y <= 410):
        app.secondGraph = False
        createSMAGraph(app)
    elif (event.x >= 240 and event.x <= 315 and
        event.y >=375 and event.y <= 410):
        app.secondGraph = True
        createIndicatorGraph(app)
    
    #checks to see if a stock button was pressed
    for y in range(len(app.stockGraphList)):
        space = 85
        if (event.x > 50+ y * space and event.x < 125+ y * space 
            and event.y > 338 and event.y < 368):
            app.stockGraph = app.stockGraphList[y]
            probabilityCoords(app)
            if app.secondGraph: createIndicatorGraph(app)
            else: createSMAGraph(app)
            suggestion(app)
            getSecondBox(app)
    
    #checks to see if a different length was chosen
    if (event.x > 50 and event.x < 125 and 
        event.y > 660 and event.y < 690):
        app.lengthRSI = 1200
        if app.secondGraph: createIndicatorGraph(app)
        else: createSMAGraph(app)
    elif (event.x > 135 and event.x < 210 and 
        event.y > 660 and event.y < 690):
        app.lengthRSI = 240
        if app.secondGraph: createIndicatorGraph(app)
        else: createSMAGraph(app)
    elif (event.x > 220 and event.x < 295 and 
        event.y > 660 and event.y < 690):
        app.lengthRSI = 60
        if app.secondGraph: createIndicatorGraph(app)
        else: createSMAGraph(app)
    elif (event.x > 305 and event.x < 380 and 
        event.y > 660 and event.y < 690):
        app.lengthRSI = 20
        if app.secondGraph: createIndicatorGraph(app)
        else: createSMAGraph(app)
    elif (event.x > 390 and event.x < 465 and 
        event.y > 660 and event.y < 690):
        app.lengthRSI = 5
        if app.secondGraph: createIndicatorGraph(app)
        else: createSMAGraph(app)

def futurePredictionsModelMode_mouseMoved(app, event):
    #checks to see if mouse is hovering over points on the first graph
    for ind in range(len(app.probCirclesList)):
        circle = app.probCirclesList[ind]
        if distance(event.x, event.y, circle.cx, circle.cy) <= circle.r:
            app.circleX = app.percentChangeList[ind]
            app.circleY = app.probabilityList[ind]
            break
    #checks to see if mouse is hovering over points on RSI graph
    if app.secondGraph:
        for ind in range(len(app.probCirclesListRSI)):
            circle = app.probCirclesListRSI[ind]
            if distance(event.x, event.y, circle.cx, circle.cy) <= circle.r:
                app.circleXRSI = app.xAxisRSI[ind]
                app.circleYRSI = app.yAxisRSI[ind]
                break
    #checks to see if mouse is hovering over points on SMA graph
    else:  
        for ind in range(len(app.probCirclesListSMA)):
            circle = app.probCirclesListSMA[ind]
            if distance(event.x, event.y, circle.cx, circle.cy) <= circle.r:
                app.circleXSMA = app.xAxisSMA[ind]
                app.circleYSMA = app.yAxisSMA[ind]
                break

#creates coordinates for the 1st graph
def probabilityCoords(app):
    app.probCirclesList = []
    app.percentChangeList = app.stockGraph.getPercentChangeList()
    app.probabilityList = app.stockGraph.getProbabilityList()
    maxX = round_decimal1(int(app.stockGraph.getPercentChangeList()[-1]+1))
    minX = round_decimal1(int(app.stockGraph.getPercentChangeList()[0]-1))
    if abs(maxX) >= abs(minX):
        minX = maxX * -1
    else:
        maxX = minX * -1
    unitYSpace = 200 / 5
    unitXSpace = 300 / (2 * maxX)

    xCoords = []
    for coor in app.percentChangeList:
        x1 = 75
        x1 += (maxX + round_decimal1(coor)) * unitXSpace
        xCoords.append(x1)
    
    yCoords = []
    for coor in app.probabilityList:
        y1 = 75
        y1 += (1 - coor) * (unitYSpace * 5)
        yCoords.append(y1)
    
    for ind in range(len(xCoords)):
        point = ProbCircles(cx=xCoords[ind], cy=yCoords[ind], r=5)
        app.probCirclesList.append(point)

#creates the FutureProbabilityModel to draw the graphs
def createFutureProbabilityModel(app):
    list = []
    for x in range(len(app.tickerFutureList)):
        stock = graphStocks(app.tickerFutureList[x], app.futureStocksBought[x])
        list.append(stock)
    app.stockGraphList = copy.copy(list)
    app.stockGraph = app.stockGraphList[0]
    probabilityCoords(app)

#gets values for second box
def getSecondBox(app):
    lowerInd = 0
    upperInd = 0
    for x in range(len(app.probabilityList)):
        if x == 0:
            continue
        elif .25 <= app.probabilityList[x] and .25 > app.probabilityList[x-1]:
            lowerInd = x
            break
    for y in range(len(app.probabilityList)):
        if y == 0:
            continue
        elif .75 <= app.probabilityList[y] and .75 > app.probabilityList[y-1]:
            upperInd = y
            break
    
    lowerChange = app.percentChangeList[lowerInd]
    upperChange = app.percentChangeList[upperInd]
    todayPrice = getTodayPrice(app.stockGraph.getTicker())
    sharesBought = app.stockGraph.getShares()
    lowerPrice = float(todayPrice) * (lowerChange / 100) + float(todayPrice)
    upperPrice = float(todayPrice) * (upperChange / 100) + float(todayPrice)
    app.upperProfit = (float(upperPrice) * float(sharesBought)) - (float(todayPrice) * float(sharesBought))
    app.lowerProfit = (float(lowerPrice) * float(sharesBought)) - (float(todayPrice) * float(sharesBought))

#creates the coordinates for the RSI graph
def createIndicatorGraph(app):
    app.probCirclesListRSI = []
    app.xAxisRSI, app.yAxisRSI = app.stockGraph.getRSI(app.lengthRSI)
    yCoords = []
    unitYSpace = 175 / ((max(app.yAxisRSI)) - (min(app.yAxisRSI)))
    for coor in app.yAxisRSI:
        y1 = 600
        y1 -= (coor-(min(app.yAxisRSI))) * unitYSpace
        yCoords.append(y1)
    
    xCoords = []
    unitXSpace = 350 / (len(app.xAxisRSI)-1)
    for i in range(len(app.yAxisRSI)):
        x1 = 50
        x1 += i * unitXSpace
        xCoords.append(x1)

    for ind in range(len(xCoords)):
        point = ProbCircles(cx=xCoords[ind], cy=yCoords[ind], r=5)
        app.probCirclesListRSI.append(point)

#decides whether to buy, sell, or hold
def suggestion(app):
    ind = 0
    for x in range(len(app.probabilityList)):
        if x == 0:
            pass
        elif .5 <= app.probabilityList[x] and .5 > app.probabilityList[x-1]:
            ind = x
    
    if app.percentChangeList[ind] <= 0 and app.yAxisRSI[-1] >= 50:
        app.suggestion = "SELL"
    elif app.percentChangeList[ind] > 0 and app.yAxisRSI[-1] < 50:
        app.suggestion = "BUY"
    else:
        app.suggestion = "HOLD"

#creates the coordinates for the SMA graph
def createSMAGraph(app):
    app.probCirclesListSMA = []
    app.xAxisSMA, app.yAxisSMA = app.stockGraph.getSMA(app.lengthRSI)
    yCoords = []
    buffer = max(app.yAxisSMA) / 10
    unitYSpace = 175 / ((max(app.yAxisSMA) + buffer) - (min(app.yAxisSMA)-buffer))
    for coor in app.yAxisSMA:
        y1 = 600
        y1 -= (coor-(min(app.yAxisSMA)-buffer)) * unitYSpace
        yCoords.append(y1)
    
    xCoords = []
    unitXSpace = 350 / (len(app.xAxisSMA)-1)
    for i in range(len(app.yAxisSMA)):
        x1 = 50
        x1 += i * unitXSpace
        xCoords.append(x1)

    for ind in range(len(xCoords)):
        point = ProbCircles(cx=xCoords[ind], cy=yCoords[ind], r=5)
        app.probCirclesListSMA.append(point)

#draws on the futurePredictionsModelMode screen
def futurePredictionsModelMode_redrawAll(app, canvas):
    canvas.create_image(350, 375, image=ImageTk.PhotoImage(app.modelsBackgroundImage))
    canvas.create_image(25, 25, image=ImageTk.PhotoImage(app.arrowImage))
    
    #create the first graph
    canvas.create_rectangle(50, 50, 400, 300,)
    canvas.create_line(225, 50, 225, 300)
    
    #creates the xAxis for first graph
    maxX = round_decimal1(int(app.percentChangeList[-1]+1))
    minX = round_decimal1(int(app.probabilityList[0]-1))
    if abs(maxX) >= abs(minX):
        minX = maxX * -1
    else:
        maxX = minX * -1
    unitXSpace = 300 / (2 * maxX)
    coordXAxis = [minX, round_decimal1(minX/2), round_decimal1(0), round_decimal1(maxX/2), maxX]
    for coor in coordXAxis:
        x1 = 75
        x1 += (maxX + coor) * unitXSpace
        canvas.create_line(x1, 295, x1, 305, width = 3)
        canvas.create_text(x1 + 15, 308, text = str(coor), 
                            font = f'Gautami 10')
    
    #creates the yAxis for the first graph
    unitYSpace = 200 / 5
    for x in range(6):
        y1 = 75 
        y1 += unitYSpace * x
        canvas.create_line(220, y1, 230, y1, width = 3)
        canvas.create_text(210, y1, text = str(((5-x)/5)), 
                            font = f'Gautami 10')

    #plot points on first graph
    for ind in range(0, len(app.probCirclesList), 10):
        circle = app.probCirclesList[ind]
        canvas.create_oval(circle.cx-circle.r, circle.cy-circle.r, 
                            circle.cx+circle.r, circle.cy+circle.r, 
                            fill = "black")
    
    #creates the first box on the side
    canvas.create_rectangle(450, 50, 650, 150)
    canvas.create_text(460, 75, text = f'Percent Change: {round_decimal2(app.circleX)}%', anchor = "w")
    canvas.create_text(460, 105, text = f'Probability of percent change ', anchor = "w")
    canvas.create_text(460, 120, text = f'being under {round_decimal2(app.circleX)}%: {round_decimal2(app.circleY)}', anchor = "w")
    canvas.create_text(225, 325, text = "Percent Change in Price", font = "Guatami 12")
    canvas.create_text(40, 137.5, text = "Probability", font = 'Guatami 12', angle = 90)

    #draws the second box
    canvas.create_rectangle(450, 165, 650, 300)
    canvas.create_text(550, 210, text = '50% chance that your profit')
    canvas.create_text(550, 230, text = f'on {app.stockGraph.getTicker()} is between')
    canvas.create_text(550, 250, text = f'{round_decimal2(app.lowerProfit)} and {round_decimal2(app.upperProfit)} dollars')

    #creates the needed buttons/titles for second graph
    canvas.create_rectangle(50, 425, 400, 600)
    canvas.create_rectangle(325, 375, 400, 410, fill = "red")
    canvas.create_text(362.5, 392.5, text = "SMA", fill = "white")
    canvas.create_rectangle(240, 375, 315, 410, fill = "blue")
    canvas.create_text(277.5, 392.5, text = "RSI", fill = "white")
    canvas.create_text(225, 645, text = "Date", font = 'Guatami 12')
    canvas.create_text(50, 30, text = f'Probability of Percent Change in {app.stockGraph.getTicker()}\'s Price Being Under a Certain Number', font = 'Guatami 12', anchor = 'w')

    #creates the length button for the second graph
    canvas.create_rectangle(50, 660, 125, 690, fill = "green")
    canvas.create_text(87.5, 675, text = "5 years", fill = "white")
    canvas.create_rectangle(135, 660, 210, 690, fill = "green")
    canvas.create_text(172.5, 675, text = "1 year", fill = "white")
    canvas.create_rectangle(220, 660, 295, 690, fill = "green")
    canvas.create_text(257.5, 675, text = "3 months", fill = "white")
    canvas.create_rectangle(305, 660, 380, 690, fill = "green")
    canvas.create_text(342.5, 675, text = "1 month", fill = "white")
    canvas.create_rectangle(390, 660, 465, 690, fill = "green")
    canvas.create_text(427.5, 675, text = "1 week", fill = "white")
    
    #creates all the stock buttons
    y = 0
    for x in app.stockGraphList:
        space = 85
        canvas.create_rectangle(50+ y * space, 338, 125+ y * space, 368, fill = "green")
        midX, midY = midPoint(50+ y * space, 125+ y * space, 338, 368)
        canvas.create_text(midX, midY, text = str(x.getTicker()), fill = "white")
        y += 1 

    if app.secondGraph:
        #create RSI graph
        canvas.create_text(10, 512.5, text = "RSI", font = 'Guatami 12', angle = 90)
        canvas.create_text(50, 405, text = f'{app.stockGraph.getTicker()} RSI Overtime', font = 'Guatami 15', anchor = 'w')
        
        #creates xAxis for RSI graph
        unitXSpace = 350 / 4
        lengthOfXAxis = len(app.xAxisRSI)
        textX = [ app.xAxisRSI[0], app.xAxisRSI[(lengthOfXAxis-1)//4], app.xAxisRSI[(lengthOfXAxis-1)//2], app.xAxisRSI[((lengthOfXAxis-1)//2)+((lengthOfXAxis-1)//4)], app.xAxisRSI[lengthOfXAxis-1] ]
        y = 0
        for x in range(5):
            x1 = 50
            x1 += unitXSpace * x
            canvas.create_line(x1, 595, x1, 605, width = 3)
            canvas.create_text(x1 + 5, 610, text = str(textX[y]), 
                                font = f'Gautami 7', angle = 45, anchor = "e")
            y += 1
        
        #creates yAxis for RSI graph
        unitYSpace = 175 / 4
        mid = ((max(app.yAxisRSI)) + (min(app.yAxisRSI)))/ 2
        textY = [ roundHalfUp(min(app.yAxisRSI)), roundHalfUp((mid + (min(app.yAxisRSI)))/ 2), roundHalfUp(mid), roundHalfUp((mid + (max(app.yAxisRSI)))/ 2), roundHalfUp(max(app.yAxisRSI)) ]
        x = 0
        for y in range(5):
            y1 =  600
            y1 -= unitYSpace * y
            canvas.create_line(45, y1, 55, y1, width = 3)
            canvas.create_text(35, y1, text = textY[x], 
                                font = f'Gautami 10')
            x+=1
        
        #plots all points on the RSI graph
        lengthStock = len(app.probCirclesListRSI) // 30
        if lengthStock < 1:
            lengthStock = 1
        for ind in range(0, len(app.probCirclesListRSI), lengthStock):
            circle = app.probCirclesListRSI[ind]
            canvas.create_oval(circle.cx-circle.r, circle.cy-circle.r, 
                                circle.cx+circle.r, circle.cy+circle.r, 
                                fill = "blue")
        
        #creates the third box on the side
        canvas.create_rectangle(450, 425, 650, 510)
        canvas.create_text(460, 440, text = f'Date: {app.circleXRSI}', anchor = "w")
        canvas.create_text(460, 475, text = f'RSI: {round_decimal2(app.circleYRSI)}', anchor = "w")
    
    elif app.secondGraph == False:
        #creates SMA graph
        canvas.create_text(10, 512.5, text = "SMA", font = 'Guatami 12', angle = 90)
        canvas.create_text(50, 405, text = f'{app.stockGraph.getTicker()} SMA Overtime', font = 'Guatami 15', anchor = 'w')
        
        #creates xAxis for SMA graph
        unitXSpace = 350 / 4
        lengthOfXAxis = len(app.xAxisSMA)
        textX = [ app.xAxisSMA[0], app.xAxisSMA[(lengthOfXAxis-1)//4], app.xAxisSMA[(lengthOfXAxis-1)//2], app.xAxisSMA[((lengthOfXAxis-1)//2)+((lengthOfXAxis-1)//4)], app.xAxisSMA[lengthOfXAxis-1] ]
        y = 0
        for x in range(5):
            x1 = 50
            x1 += unitXSpace * x
            canvas.create_line(x1, 595, x1, 605, width = 3)
            canvas.create_text(x1 + 5, 610, text = str(textX[y]), 
                                font = f'Gautami 7', angle = 45, anchor = "e")
            y += 1
        
        #creates yAxis fro SMA graph
        unitYSpace = 175 / 4
        buffer = (max(app.yAxisSMA) / 10)
        mid = ((max(app.yAxisSMA)+buffer) + (min(app.yAxisSMA)-buffer))/ 2
        textY = [ roundHalfUp(min(app.yAxisSMA)-buffer), roundHalfUp((mid + (min(app.yAxisSMA)-buffer))/ 2), roundHalfUp(mid), roundHalfUp((mid + (max(app.yAxisSMA)+buffer))/ 2), roundHalfUp(max(app.yAxisSMA)+buffer) ]
        x = -1
        for y in range(5):
            y1 =  425
            y1 += unitYSpace * y
            canvas.create_line(45, y1, 55, y1, width = 3)
            canvas.create_text(33, y1, text = str(textY[x]), 
                                font = f'Gautami 7')
            x-=1
        
        #plots points on the SMA graph
        lengthStock = len(app.probCirclesListSMA) // 30
        if lengthStock < 1:
            lengthStock = 1
        for ind in range(0, len(app.probCirclesListSMA), lengthStock):
            circle = app.probCirclesListSMA[ind]
            canvas.create_oval(circle.cx-circle.r, circle.cy-circle.r, 
                                circle.cx+circle.r, circle.cy+circle.r, 
                                fill = "red")
        
        #creates third box on the side
        canvas.create_rectangle(450, 425, 650, 510)
        canvas.create_text(460, 440, text = f'Date: {app.circleXSMA}', anchor = "w")
        canvas.create_text(460, 475, text = f'SMA: {round_decimal2(app.circleYSMA)}', anchor = "w")

    #creates 4th box on the side
    canvas.create_rectangle(450, 525, 650, 600)
    canvas.create_text(550, 562.5, text = app.suggestion, font = "Guatami 45 bold")

runApp(width=700, height=750)