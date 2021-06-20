import socket
import os
import json
import hashlib
import threading
import sys
from signal import SIGTERM
from re import match as re_match
from argparse import ArgumentParser
from random import randint as random_int
from time import sleep
import random
import mss
import mss.tools

import tkinter
import pyautogui
from PIL import Image
from io import BytesIO
from array import array
from PIL import Image as ImageModule
from PIL import ImageTk
from datetime import datetime, timedelta
from PIL import ImageFile

tk = tkinter.Tk()
screen_width = tk.winfo_screenwidth()
screen_height = tk.winfo_screenheight()
canvas = tkinter.Canvas(tk, width=screen_width, height=screen_height)
canvas.pack()

FPS = 4
ImageFile.LOAD_TRUNCATED_IMAGES = True

def getscreen():
	with mss.mss() as sct:
		monitor = sct.monitors[1]
		im = sct.grab(monitor)
		raw_bytes = mss.tools.to_png(im.rgb, im.size)
		im1 = Image.open(BytesIO(raw_bytes))
		im1 = im1.resize((1280,720))
		img_byte_arr = BytesIO()
		im1.save(img_byte_arr, format='JPEG', optimize=True, subsampling=0, quality=10)
		return img_byte_arr.getvalue()

class Argparser(ArgumentParser):
	def error(self, message):
		self.print_help()
		sys.stderr.write(f"\nError: {message}\n")
		sys.exit(2)


def parse_args():
	argparser = Argparser()
	argparser.add_argument('-i', '--ip', help="Server IP", required=True, action="store")
	argparser.add_argument('-p', '--port', help="Server Port", type=int, required=True, action="store")
	argparser.add_argument('-k', '--key', help="Chat key file", action="store")
	return argparser.parse_args()

args = parse_args()
ipv4, port = args.ip, args.port
if not re_match(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", ipv4):
	exit("Given IP is invalid")

def rcv_cmd(connection):
	data1 = bytearray()
	while True:
		try:
			data = connection.recv(1)
			if data == b'\n':
				return data1.decode('utf-8')
			data1 += data
			if len(data1) > 1536 or not len(data):
				return None
		except:
			messagebox.showwarning(title="No connection", message="Connection has been dropped by server")
			os.kill(os.getpid(), SIGTERM)

def wait_rcv_cmd(connection):
	while True:
		data = rcv_cmd(connection)
		if not data:
			continue
		return data

def snd_cmd(connection, cmd):
	connection.send((cmd + '\n').encode('utf-8'))

def hash_md5(data):
	return hashlib.md5(data.encode('utf-8')).hexdigest()
	
def inttoarr(a,l):
	arr = bytearray()
	for i in range(l):
		arr.append(a & 255)
		a = a >> 8
	return arr
	
def arrtoint(a):
	res = 0
	for elem in a[::-1]:
		res = (res << 8) | elem
	return res
	
def write_data(connection, data):
	connection.send(inttoarr(len(data),1))
	for elem in data:
		connection.send(inttoarr(len(elem),4))
		connection.send(elem)
		
def read_data(connection):
	arr_len = connection.recv(1)[0]
	ret = []
	for i in range(arr_len):
		cur_len = arrtoint(connection.recv(4))
		ret.append(connection.recv(cur_len,socket.MSG_WAITALL))
	return ret

def networkloop(tk1):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ipv4, port))
	mykey = ''
	for i in range(4):
		mykey += chr(random.randint(65,80))
	write_data(sock,[
	bytearray('set-key'.encode()),
	bytearray(mykey.encode())])
	print('your key: ',mykey)
	print('S or C?')
	if(input()=='S'):
		while True:
			scr_data = getscreen()
			write_data(sock,[
			bytearray('screen'.encode()),
			getscreen()
			])
			print(datetime.now(),' ',len(scr_data))
			sleep(1.0/FPS)
	else:
		print('enter-key:')
		key = input()
		write_data(sock,[
		bytearray('get-scr'.encode()),
		bytearray(key.encode())])
		while True:
			#write_data(sock,[
			#bytearray('get-scr'.encode()),
			#bytearray(key.encode())
			#])
			data = read_data(sock)[0]
			print(datetime.now(),' ',len(data))
			image = Image.open(BytesIO(data))
			image = image.resize((screen_width,screen_height))
			photo = ImageTk.PhotoImage(image)
			canvas.delete('all')
			image = canvas.create_image(0, 0, anchor='nw',image=photo)
			sleep(1.0/FPS)

# ENTRY
threading.Thread(target=networkloop, args=(tk,)).start()
tk.mainloop()

