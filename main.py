from fastapi import FastAPI, HTTPException, Body
from datetime import date
from pymongo import MongoClient
from pydantic import BaseModel

DATABASE_NAME = "exceed07"
COLLECTION_NAME = "reservation_rachata"
MONGO_DB_URL = f"mongodb://exceed07:8td6VF6w@mongo.exceed19.online"   # mongodb://localhost
MONGO_DB_PORT = 8443 
#mongodb://exceed07:8td6VF6w@mongo.exceed19.online:8443/?authMechanism=DEFAULT

class Reservation(BaseModel):
    name : str
    start_date: date
    end_date: date
    room_id: int


client = MongoClient(f"{MONGO_DB_URL}:{MONGO_DB_PORT}/?authMechanism=DEFAULT")
#client = MongoClient(f"mongodb://exceed07:8td6VF6w@mongo.exceed19.online:8443/?authMechanism=DEFAULT")

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]

app = FastAPI()



def room_avaliable(room_id: int, start_date: str, end_date: str):
    query={"room_id": room_id,
           "$or": 
                [{"$and": [{"start_date": {"$lte": start_date}}, {"end_date": {"$gte": start_date}}]},
                 {"$and": [{"start_date": {"$lte": end_date}}, {"end_date": {"$gte": end_date}}]},
                 {"$and": [{"start_date": {"$gte": start_date}}, {"end_date": {"$lte": end_date}}]}]
            }
    
    result = collection.find(query, {"_id": 0})
    list_cursor = list(result)

    return not len(list_cursor) > 0


@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name: str):
    res = collection.find({'name': name})
    return res

@app.get("/reservation/by-room/{room_id}")
def get_reservation_by_room(room_id: int):
    res = collection.find({'room_id': room_id})
    return res

@app.post("/reservation")
def reserve(reservation : Reservation):
    if(reservation.room_id > 10 or reservation.room_id < 1):
         raise HTTPException(status_code=400)
    if(reservation.start_date > reservation.end_date):
        raise HTTPException(status_code=400)
    
    if(not room_avaliable(reservation.room_id,str(reservation.start_date),str(reservation.end_date))):
          raise HTTPException(status_code=400)
    #print(reservation.start_date)
    collection.insert_one({
            "name": reservation.name,
            "start_date": str(reservation.start_date),
            "end_date": str(reservation.end_date),
            "room_id": reservation.room_id
})
    return

@app.put("/reservation/update")
def update_reservation(reservation: Reservation, new_start_date: date = Body(), new_end_date: date = Body()):
    if(reservation.room_id > 10 or reservation.room_id < 1):
        raise HTTPException(status_code=400)
    if(reservation.start_date > reservation.end_date):
        raise HTTPException(status_code=400)
    if(new_start_date > new_end_date):
        raise HTTPException(status_code=400)
    if(not room_avaliable(reservation.room_id,str(new_start_date),str(new_end_date))):
        raise HTTPException(status_code=400)
    
    
    split_date = str(new_start_date).split('-')
    if(len(split_date[1]) == 1):
        split_date[1] = '0'+split_date[1]
    if(len(split_date[2]) == 1):
        split_date[2] = '0'+split_date[2]
    new_start_date = split_date[0]+'-'+split_date[1]+'-'+split_date[2]
    
    split_date = str(new_end_date).split('-')
    if(len(split_date[1]) == 1):
        split_date[1] = '0'+split_date[1]
    if(len(split_date[2]) == 1):
        split_date[2] = '0'+split_date[2]
    new_end_date = split_date[0]+'-'+split_date[1]+'-'+split_date[2]

    collection.update_one({
            "name": reservation.name,
            "start_date": str(reservation.start_date),
            "end_date": str(reservation.end_date),
            "room_id": reservation.room_id
},{'$set':{'start_date':str(new_start_date),'end_date':str(new_end_date)}})
    return

@app.delete("/reservation/delete")
def cancel_reservation(reservation: Reservation):
    collection.delete_one({
            "name": reservation.name,
            "start_date": str(reservation.start_date),
            "end_date": str(reservation.end_date),
            "room_id": reservation.room_id
})
    return