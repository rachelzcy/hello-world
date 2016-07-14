import pika
import json
import MySQLdb
from gcm import GCM

class MyDatabase:
	db = None
	def _init_(self):
		self.connect()
		return
	def connect(self):
		db = MySQLdb.connect(
			"localhost",
             		"root",
             		"931211",
             		"iems5722"
		)
		return


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='chat', durable=True)

def callback(ch, method, properties, body):
       	print body
	data = json.loads(body)
	#chatroom_id = data["chatroom_id"]
	user_id = data["user_id"]
	chatroom = data["chatroom"]
	message = data["message"] 
	db = MySQLdb.connect(
             "localhost",
             "root",
             "931211",
             "iems5722"
    )
	cursor = db.cursor()
#	query = "select name from chatrooms where chatroom_id=%d;" %(chatroom_id)
#	cursor.execute(query)
#	chatrooms = cursor.fetchall()
#	chatroom_name = chatrooms[0].get('name')
		
	token = ""
	query2 = "select token from push_tokens where user_id=%s;" %(user_id)
	cursor.execute(query2)
	tokens = cursor.fetchall()
	print query2	
	#if tokens:
	for token in tokens:
		tok = token[0]
		API_KEY = 'AIzaSyCA2wBd4HXLGlUcqUGb6PTKkhH7fybXX0Y'
        	print tok
		gcm = GCM(API_KEY)
		reg_ids = [tok]
		notification = dict(
			chatroom_name=chatroom
#			,chatroom_id=chatroom_id
	#		,user_id=user_id
			,message=message
		)
        
		response = gcm.json_request(registration_ids=reg_ids,
				data=notification)
		print response
channel.basic_consume(callback, queue='chat', no_ack=True)
channel.start_consuming()
