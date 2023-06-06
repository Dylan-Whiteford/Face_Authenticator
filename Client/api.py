
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route("/")
def hello_world():
    return "Hello, World!"

import datetime
import pymongo

#today - datetime.timedelta(days = 1)

@app.route("/GetByDay" ,methods = [ 'GET'])
def GetByDay():

    date = datetime.datetime.now()
    client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
    db = client["Face_Tracker"]
    logs = db["Face_Log"]

    start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = date.replace(hour=23, minute=59, second=59, microsecond=999)


    # Per minute
    pipeline = [
        {"$match":{
            "time_captured":{"$gte": start_time, "$lt":  end_time},
        }},
        {"$group":{ 
            "_id" :  {
                "year": {"$year": "$time_captured" },
                "month": {"$month": "$time_captured"}, 
                "day": {"$dayOfMonth": "$time_captured"},
                "hour": { "$hour": "$time_captured" },
                "minute": { "$minute": "$time_captured" },
                "face": "$face_id",
            },
            "count": {"$sum": 1} ,
            "doc":{"$first":"$$ROOT"}

        }},

    ]
    data = []
    for log in logs.aggregate(pipeline ):

        interval = datetime.timedelta(minutes = 1)
        start = log['doc']["time_captured"]
        end = start + interval
        plotpoint = (start, end, str(log['doc']["face_id"]))
        data.append(plotpoint)

    cats_raw = logs.aggregate( [ 
        {"$match":{
            "time_captured":{"$gte": start_time, "$lt":  end_time},
        }},
        {"$group": { "_id" : "$face_id" } } 
    ])

    cats={}
    col={}
    catlabels = []
    count = 0
    for uniq in cats_raw:
        print(uniq)
        col[uniq["_id"]] = "C"+str(count)
        count+=1
        cats[uniq["_id"]] = count
        catlabels.append(uniq["_id"])

    print(data)
    print(cats)
    print(col)
    print(catlabels)
    client.close()

    return {
        "data": data,
        "cats":cats,
        "col":col,
        "catlabels":catlabels,
        "type":"day"
    }


@app.route("/GetByHour",methods = [ 'GET'])
def GetByHour():

    date = datetime.datetime.now()
    client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
    db = client["Face_Tracker"]
    logs = db["Face_Log"]

    start_time = date.replace( minute=0, second=0, microsecond=0)
    end_time = date.replace( minute=59, second=59, microsecond=999)


    # Per second
    pipeline = [
        {"$match":{
            "time_captured":{"$gte": start_time, "$lt":  end_time},
        }},
        {"$group":{ 
            "_id" :  {
                "year": {"$year": "$time_captured" },
                "month": {"$month": "$time_captured"}, 
                "day": {"$dayOfMonth": "$time_captured"},
                "hour": { "$hour": "$time_captured" },
                "minute": { "$minute": "$time_captured" },
                "second": { "$second": "$time_captured" },
                "face": "$face_id",
            },
            "count": {"$sum": 1} ,
            "doc":{"$first":"$$ROOT"}

        }},

    ]
    data = []
    for log in logs.aggregate(pipeline ):

        interval = datetime.timedelta(seconds= 1)
        start = log['doc']["time_captured"]
        end = start + interval
        plotpoint = (start, end, str(log['doc']["face_id"]))
        data.append(plotpoint)

    cats_raw = logs.aggregate( [ 
        {"$match":{
            "time_captured":{"$gte": start_time, "$lt":  end_time},
        }},
        {"$group": { "_id" : "$face_id" } } 
    ])

    cats={}
    col={}
    catlabels = []
    count = 0
    for uniq in cats_raw:
        print(uniq)
        col[uniq["_id"]] = "C"+str(count)
        count+=1
        cats[uniq["_id"]] = count
        catlabels.append(uniq["_id"])

    print(data)
    print(cats)
    print(col)
    print(catlabels)
    client.close()

    return {
        "data": data,
        "cats":cats,
        "col":col,
        "catlabels":catlabels,
        "type":"day"
    }