from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import RangeTool,PanTool,WheelZoomTool,HoverTool,BoxZoomTool
#have to check TapTool
from bokeh.models import TapTool,WheelPanTool,SaveTool,ZoomInTool,ZoomOutTool,ResetTool
from bokeh.layouts import column,layout,gridplot
import stockData

def drawOpenGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['Open'],legend_label=symbolName+" Open",line_width=2,color = color)
#code for drawing the close prices of the stock available in the dataframe
def drawCloseGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['Close'],legend_label=symbolName+" Close",line_width=2,color=color)
#code for drawing the high prices
def drawHighGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['High'],legend_label=symbolName+" High",line_width=2,color=color)
#code for drawing the low prices
def drawLowGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['Low'],legend_label=symbolName+" Low",line_width=2,color=color)
#code for drawing a combined candle stick graph to consisting of 
#high low prices as segments
#the blocks represent opening and closing prices
def drawCombinedGraph(symbolName,plot,df,timeInterval,color):
    #this draws the segemnt from the opening to the closing price
    plot.segment(df.Datetime,df.High,df.Datetime,df.Low,color=color,legend_label=symbolName+" Combined")
    #different plots for open price above close price and 
    #close price above open price
    #boolean arrs to show whether opening price is above or below closing price
    barWidth = timeInterval/2
    priceInc = df.Close > df.Open 
    priceDec = df.Open > df.Close 
    #add legend lable here later perhaps?
    plot.vbar(df.Datetime[priceDec],barWidth,df.Open[priceDec],df.Close[priceDec],color="#eb3c40")
    plot.vbar(df.Datetime[priceInc],barWidth,df.Open[priceInc],df.Close[priceInc],color="#00ff00",
              line_color="00ffff",line_width=2)
def drawCurGraphAndTable(dataFrameDict,curGraphSelection):
    #creating the panTool and wheel zoom tool which is available to 
    #naigate across the graph
    #from bokeh.models import RangeTool,PanTool,WheelZoomTool,HoverTool,BoxZoomTool
    #have to check TapTool
    #from bokeh.models import TapTool,WheelPanTool,SaveTool,ZoomInTool,ZoomOutTool
    hoverTool = HoverTool(
        tooltips = [('date','$x{%F}'),('price','$y{(0.00 a)}')],
        formatters={'$x':'datetime'}
    )
    tools = [PanTool(),WheelZoomTool(),hoverTool,BoxZoomTool(),
            TapTool(),WheelPanTool(),SaveTool(),ZoomInTool(),ZoomOutTool(),ResetTool()]

    #creating the figure in which the graph is actually drawn
    plot = figure(x_axis_label="Date Time",y_axis_label="Price",
                x_axis_type="datetime",toolbar_location="right",
                tools= tools)
    #setting the main graph to stretch in both the x axis direction and y direction to 
    #fill the space alloted
    plot.sizing_mode = "stretch_both"
    
    #creating the mini graph available below the main graph which is
    #used for zooming in and out of the graph
    rangePlot = figure(height=100,x_axis_type="datetime",
                        y_axis_type=None,toolbar_location=None,
                        background_fill_color="#efefef")
    #setting the mini graph to only stretch in the x direction
    rangePlot.sizing_mode = "stretch_width"

    rangeTool = RangeTool(x_range=plot.x_range)
    rangeTool.overlay.fill_color = "navy"
    rangeTool.overlay.fill_alpha = 0.2
    #adding the rangeTool which allows us to zoom in and out of the main graph to the mini graph
    rangePlot.add_tools(rangeTool)
    rangePlot.toolbar.active_multi = 'auto'

    for symbolName in curGraphSelection:
        curDict = curGraphSelection[symbolName]
        duration_req = curDict['graphDuration']

        df = dataFrameDict[symbolName]
        timeInterval = 60*1000 
        #time interval corresponding to one min in miili seconds 
        #this is used to find the width of the bar graph 

        #time period for which graph is drawn
        timePeriod = curDict['graphDuration']
        graphCont = curDict['graphCont']
        colors = curDict['color']
        for elm in graphCont:
            if graphCont[elm] :
                match elm:
                    case 'OPEN':
                        drawOpenGraph(symbolName,plot,df,colors['OPEN'])
                        drawOpenGraph(symbolName,rangePlot,df,colors['OPEN'])
                    case 'CLOSE':
                        drawCloseGraph(symbolName,plot,df,colors['CLOSE'])
                        drawCloseGraph(symbolName,rangePlot,df,colors['CLOSE'])
                    case 'HIGH':
                        drawHighGraph(symbolName,plot,df,colors['HIGH'])
                        drawHighGraph(symbolName,rangePlot,df,colors['HIGH'])
                    case 'LOW':
                        drawLowGraph(symbolName,plot,df,colors['LOW'])
                        drawLowGraph(symbolName,rangePlot,df,colors['LOW'])
                    case 'COMBINED':
                        drawCombinedGraph(symbolName,plot,df,timeInterval,colors['COMBINED'])
                        drawCombinedGraph(symbolName,rangePlot,df,timeInterval,colors['COMBINED'])

    total = column(plot,rangePlot,sizing_mode="stretch_both")
    script,div = components(total)
        
    #modifying div generated by bokeh library so that we can add the styling from our css file
    div = div[:-7] + ' class="GraphDiv" ></div>'
    return (script,div)

def drawStockIndicesGraph():
    indices = ['NIFTY 50','NIFTY NEXT 50','NIFTY BANK','NIFTY IT']
    colors = ['#d04848','#f3b95f','#6895d2','#37b5b6']
    plotArr = []
    hoverTool = HoverTool(
        tooltips = [('date','$x{%F}'),('price','$y{(0.00 a)}')],
        formatters={'$x':'datetime'}
    )

    tools = [PanTool(),WheelZoomTool(),hoverTool,BoxZoomTool(),
            TapTool(),WheelPanTool(),SaveTool(),ZoomInTool(),ZoomOutTool(),ResetTool()]
    for i in range(len(indices)):
        symbolName = indices[i]
        curCol = colors[i]
        curDf = stockData.getDailyData(symbolName)
        curPlot = figure(x_axis_label="Date Time",y_axis_label="Open Price",
                x_axis_type="datetime",title=symbolName,tools = tools)
        curPlot.title.align = "center"
        curPlot.title.text_font_size = "20px"
        curPlot.sizing_mode = 'stretch_width'
        drawOpenGraph(symbolName,curPlot,curDf,curCol)
        plotArr.append(curPlot)
    grid = gridplot(plotArr,ncols = 2)
    grid.sizing_mode = 'stretch_width'
    (script,div) = components(grid)
    div = div[:-7] + ' class="StockIndices" ></div>'
    return (script,div)