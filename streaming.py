#!/usr/bin/python3



###################################Video Feed##################################################################################

def video_streamer():

	#class to create camera object
	class VideoCamera(object):
		def __init__(self):
			# Open a camera
			try:
				self.cap = cv2.VideoCapture(0)
			except:
				self.cap = cv2.VideoCapture(1)
				

		def __del__(self):
			self.cap.release()

		def get_frame(self):
			ret, frame = self.cap.read()
			#ret is boolean, true if successfully captures frame

			if ret:
				ret, jpeg = cv2.imencode('.jpg', frame)
				return jpeg.tobytes()

			else:
				return None


	#if websocket gets message, we know receiver exists, so set reciever to true
	def on_message(ws, message):
		global pong
		global receiver_exists
		try:
			if message == 'pong':
				#global pong
				#global receiver_exists
				pong = True
				receiver_exists = True
				print('got pong')
			   
			if message == 'newFeed':
				#global pong
				#global receiver_exists
				pong = False
				receiver_exists = False
				print('got new feed request')
		except:
			pass

	def on_error(ws, error):
		print("### error ###", error)

	def on_close(ws):
		print("### closed ###")
		time.sleep(1)

	def on_open(ws):
		print('### connected ###')
		#this thread runs forever, check for recveiver, start camera if true, and if camera isnt already going
		async def stream(*args):
			video_camera = None
			while True:
				global receiver_exists
				if not receiver_exists:# returns to begining of while loop if no reciever. (continue does this)
					if video_camera is not None:
						print('### release camera ###')
						del video_camera
						video_camera = None
					time.sleep(1)
					continue

				if video_camera is None:
					print('### start capturing ###')
					while video_camera is None:
						video_camera = VideoCamera()

				frame = video_camera.get_frame()
					
				if frame != None:
					try:
						await ws.send(frame, websocket.ABNF.OPCODE_BINARY)
					except Exception as e:
						break
				if frame is None:
					rebootStream()

			print('### closing stream thread ###')
			
		#send ping every 2 seconds so that browsers can respond with pong if they are there
		def ping(*args):

			pongCounter = 0
			while True:
				ws.send('ping')
				global pong
				pong = False
				global receiver_exists
				time.sleep(2) #send ping every 2 seconds
				if pong:
					pongCounter = 0
				if not pong:
					pongCounter = pongCounter + 1
				if pongCounter == 2:
					receiver_exists = False
			print('### closing ping thread ###')

		asyncio.get_event_loop().run_until_complete(stream())
		asyncio.get_event_loop().run_forever()
		thread.start_new_thread(ping, ())
    #main while loop of this thread. Opens and intializes websocket
	def videoSocket():
		while True:
			if run_environment == 'local':
				uri = f"{wsPrefix}stream/{localSerial}/"
			else:
				uri = f"{wsPrefix}stream/{deviceSpecificVals.machineSerial}/?{deviceSpecificVals.token}"
			
			ws = websocket.WebSocketApp(uri,
							  on_open = on_open,
							  on_message = on_message,
							  on_error = on_error,
							  on_close = on_close)

			ws.run_forever()
				
	print('connecting to video socket.....')
	videoSocket()

def rebootStream():
	new_thread = threading.Thread(target=video_streamer)

	if new_thread.is_alive():
		new_thread.join()
		time.sleep(2)
		new_thread.start()
		return

if __name__== "__main__":
	import os #for power circuit
	import time
	import deviceSpecificVals
	import ESPversion
	import threading
	import subprocess
	import threshVals
	import asyncio
	from random import randint
	from datetime import datetime
	try:
		import cv2
	except:
		print('cv2 error')
		pass
	import base64
	import websocket
	try:
		import thread
	except ImportError:
		import _thread as thread
	import re

	
	######################################## DEV PRODUCTION or LOCAL #############################################
	run_environment = 'dev' #options are 'local' 'prod' 'dev'
	

	if run_environment == 'dev':
		urlPrefix = 'http://138.197.166.169/'
		wsPrefix = 'ws://138.197.166.169/'
	if run_environment == 'local':
		#to test locally, on laptop, do python manage.py runserver 0.0.0.0:8000, then access ip of laptop with ip:8000
		urlPrefix = 'http://192.168.100.109:8000/'
		wsPrefix = 'ws://192.168.100.109:8000/'
		localSerial = '1927-01-0002'


	######################  GLOBAL VARIABLES ##############################
	serialNo = deviceSpecificVals.machineSerial
	machineType = deviceSpecificVals.machineType
	pong = False
	receiver_exists = False


	#video stream thread
	thread9 = threading.Thread(target=video_streamer)
	thread9.start()

