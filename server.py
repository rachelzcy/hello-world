from flask import Flask
import MySQLdb
from flask import jsonify
from flask import request
from datetime import datetime
import pika
import sys
import json
import cgi
import base64

app = Flask(__name__)
@app.route('/')
def hello_world():
 return 'Hello World!'


@app.route('/iems5722/get_chatrooms')
def api_get_chatrooms():
    #connect to database
    db = MySQLdb.connect(
             "localhost",
             "root",
             "931211",
             "iems5722"
    )
    cursor = db.cursor()

    #prepare and execute the query
    query = "SELECT * FROM chatrooms"
    cursor.execute(query)

    #retrieve the data and send respense
    chatrooms = cursor.fetchall()

    if chatrooms is None :
       return jsonify(status="ERROR",message="<error message>")

    chatroom=[]
    for c in chatrooms:
	chatroom.append(dict(id=c[0],name=c[1]))
    return jsonify(data=chatroom,status="OK")

@app.route('/iems5722/get_messages',methods=['GET'])
def get_messages():

    db = MySQLdb.connect(
             "localhost",
             "root",
             "931211",
             "iems5722"
    )
    cursor = db.cursor()
   
    #two inputs
    chatroom_id = request.args.get("chatroom_id")
    page = request.args.get("page")
    if chatroom_id is None or page is None:
       return jsonify(status="ERROR",message="<error message>")
   
    query = "SELECT message, name, timestamp, user_id, flag, latitude, longitude  FROM messages WHERE chatroom_id = %s order by id desc"
    cursor.execute(query,chatroom_id)
    
    messages = cursor.fetchall()
    totalpage = len(messages)/5
    if(len(messages)%5>0):
        totalpage = totalpage + 1
    if messages is None:
       return jsonify(status="ERROR",message="<error message>")

    chatmessage = []
    for i in range((int(page)-1)*5,(int(page)-1)*5+5):
     if(len(messages)>i):
        chatmessage.append(dict(message=messages[i][0],name=messages[i][1],timestamp=messages[i][2].strftime('%y-%m-%d %H:%M'),user_id=messages[i][3],flag=messages[i][4],latitude=messages[i][5],longitude=messages[i][6]))
   

    message_data = {}
    message_data.update(dict(current_page=int(page)))
    message_data.update(dict(messages=chatmessage))
    message_data.update(dict(total_pages=totalpage))
    return jsonify(data=message_data,status="OK")
    
@app.route('/iems5722/send_message',methods=['POST'])
def send_message():
    chatroom_id = int(request.form.get("chatroom_id"))
    user_id = int(request.form.get("user_id"))
    name = request.form.get("name")
    message = request.form.get("message")
    flag = int(request.form.get("flag"))
    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))
    db = MySQLdb.connect(
             "localhost",
             "root",
             "931211",
             "iems5722"
    )
    cursor = db.cursor() 
    timestamp = datetime.now().strftime('%y-%m-%d %H:%M')
    query = "INSERT INTO messages VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(chatroom_id,user_id,name,message,timestamp,flag,latitude,longitude))
    query2 = "select * from chatrooms where id = %s"
    cursor.execute(query2,chatroom_id)
    chatroom = cursor.fetchone()
    data = dict(chatroom=chatroom[1],message=message,flag = flag,timestamp = timestamp,user_id=user_id,latitude = latitude, longitude = longitude)
    json_string = json.dumps(data)
    db.commit()
    if chatroom_id is None or user_id is None or name is None or message is None or flag is None or latitude is None or longitude is None:
       return jsonify(status="ERROR",message="<error message>")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #channel.queue_declare(queue='chat')

    channel.basic_publish(exchange='',routing_key='chat' ,body=json_string)

    connection.close()
    return jsonify(status="OK")

@app.route('/iems5722/submit_push_token',methods=['POST'])
def push_token():
    user_id = int(request.form.get("user_id"))
    token = request.form.get("token")
    db = MySQLdb.connect(
             "localhost",
             "root",
             "931211",
             "iems5722"
    )
    cursor = db.cursor()
    query = "INSERT INTO push_tokens VALUES(null,%s,%s) on duplicate key update token ='%s';"
    cursor.execute(query,(user_id,token,token))
    db.commit()
    if user_id is None or token is None:
       return jsonify(dict(status="ERROR",message="<error message>"))
    return jsonify(dict(status="OK"))
 
         
@app.route('/test')
def test():
 return 'test page'

if __name__ == '__main__':
 app.debug = True
 app.run(host='0.0.0.0')
