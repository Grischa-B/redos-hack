import socket
import threading
import sqlite3
import sys
import json
import hashlib
from argparse import ArgumentParser
from errno import EADDRNOTAVAIL, EADDRINUSE
from re import match as re_match
from random import randint as random_int, choice as random_choice
from time import time, sleep


def rcv_cmd(connection):
    data1 = bytearray()
    while True:
        try:
            data = connection.recv(1)
            if data == b'\n':
                return data1.decode('utf-8')
            if not len(data):
                break
            data1 += data
            if len(data1) > 1536:
                return
        except socket.timeout:
            if connection.fileno() == -1:
                return False
            continue
        except:
            return "Closed"


def wait_rcv_cmd(connection):
    while True:
        data = rcv_cmd(connection)
        if data == "Closed":
            return
        if not data:
            continue
        return data

def snd_cmd(connection, cmd):
    connection.send((str(cmd) + '\n').encode('utf-8'))

def hash_md5(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

connections_handler = []

class Argparser(ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write(f"\nError: {message}\n")
        sys.exit(2)

def parse_args(socket_host):
    argparser = Argparser()
    argparser.add_argument('-i', '--ip', help="IP to listen [Default value - " + socket_host + "]", default=socket_host)
    argparser.add_argument('-p', '--port', help="Port to listen", type=int, required=True, action="store")
    return argparser.parse_args()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
args = parse_args(socket.gethostbyname(socket.gethostname()))
ipv4, port = args.ip, args.port
if not re_match(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", ipv4):
    exit("Given IP is invalid")

try:
    server_socket.bind((ipv4,port))
except PermissionError:
    exit(f"Permission denied for port {port}")
except OverflowError:
    exit("Port must be in range of 0-65535")
except OSError as e:
    if e.errno == EADDRNOTAVAIL:
        exit(f"Could not listen on {ipv4}")
    elif e.errno == EADDRINUSE:
        exit(f"Port {port} is already in use")

server_socket.listen()
print('Listening at', str(ipv4) + ':' + str(port) + ' ...')

def findbykey(key):
    for elem in connections_handler:
        if elem.key == key:
            return elem

def findclients(key):
    ret = []
    for elem in connections_handler:
        if elem.hostkey == key:
            ret.append(elem)
    return ret

class ConnectionHandler:
    def __init__(self, connection):
        self.key = ''
        self.hostkey = ''
        self.image = ''
        self.connection = connection

    def connection_handler(self):
        print('connected')
        try:
            while True:
                sleep(.1)
                data = read_data(self.connection)
                if data[0].decode()=='set-key':
                    self.key = data[1].decode();
                if data[0].decode()=='screen':
                    l = threading.Lock()
                    with l:
                        cls = findclients(self.key)
                        for elem in cls:
                        	write_data(elem.connection,[data[1]])
                if data[0].decode()=='get-scr':
                    self.hostkey = data[1].decode()
        except:
            pass
        try:
            self.connection.close()
        except:
            pass
        try:
            connections_handler.pop(connections_handler.index(self))
        except:
            pass

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

while True:
    new_connection, _ = server_socket.accept()
    new_connection_ip = new_connection.getsockname()[0]
    handler = ConnectionHandler(new_connection)
    connections_handler.append(handler)
    threading.Thread(target=handler.connection_handler).start()

