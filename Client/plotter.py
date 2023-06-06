import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection

import queries
def plot(getbywhat):
    if(getbywhat=="day"):
        data, cats,colormapping,catLabels,interval = queries.GetByDay(dt.datetime.now() -dt.timedelta(hours=1) )
    
    elif(getbywhat=="hour"):
        data, cats,colormapping,catLabels,interval = queries.GetByhour(dt.datetime.now() -dt.timedelta(hours=1) )


    verts = []
    colors = []
    for d in data:
        v =  [(mdates.date2num(d[0]), cats[d[2]]-.4),
            (mdates.date2num(d[0]), cats[d[2]]+.4),
            (mdates.date2num(d[1]), cats[d[2]]+.4),
            (mdates.date2num(d[1]), cats[d[2]]-.4),
            (mdates.date2num(d[0]), cats[d[2]]-.4)]
        verts.append(v)
        colors.append(colormapping[d[2]])

    bars = PolyCollection(verts, facecolors=colors)

    fig, ax = plt.subplots()
    ax.add_collection(bars)
    ax.autoscale()

    if(interval=="hour"):
        loc = mdates.MinuteLocator(interval=1)
        h_fmt = mdates.DateFormatter('%H:%M:%S')
    elif(interval=="day"):
        loc = mdates.MinuteLocator(interval=10)
        h_fmt = mdates.DateFormatter('%H:%M:%S')

    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(h_fmt)

    ax.set_yticks(range(1,len(cats)+1 ))
    ax.set_yticklabels(catLabels)
    fig.autofmt_xdate()
    plt.show()

plot("day")