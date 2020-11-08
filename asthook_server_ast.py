
from multiprocessing.connection import Listener
import pickle
from asthook import DIR
from asthook.static.ast import ast, Register
from asthook.utils import *
from asthook.static.module import ModuleStatic
import _thread
import sys


CALL = []

def proc(conn, index):
    while True:
        msg = conn.recv()
        if msg == 'args':
            msg = conn.recv()
            args = pickle.loads(msg)
            #print(args)
            basepath = '%s/%s/' % (
            DIR,
            args.app.split('/')[-1])
            CALL[index]["args"] = args
            CALL[index]["basepath"] = basepath
            conn.send("args OK")
        elif msg == 'output':
            msg = conn.recv()
            Output.replace(pickle.loads(msg), index)
            #print(Output.get_store(index))
            conn.send("output OK")
        elif msg == 'run':
            Register.set_instance(index)
            app = CALL[index]["args"].app
            basepath = CALL[index]["basepath"]
            args = CALL[index]["args"]
            ModuleStatic(app, "%s" % (basepath), args)
            ast(basepath, app, args, index, conn)
            Output.print_static_module(index)
            conn.send(Output.none_print(index))
        elif msg == 'close':
            conn.close()
            break




def main(server, port):
    global CALL

    Output.init()
    address = (server, port)     # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey=b'madkey')
    while True:
        conn = listener.accept()
        CALL.append({})
        index = len(CALL) - 1
        print(f'connection accepted from {listener.last_accepted}')
        _thread.start_new_thread(proc, (conn, index,))
    listener.close()

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} <ip> <port>")
        sys.exit(1)
    main(sys.argv[1], int(sys.argv[2]))
#from multiprocessing.connection import Client
#
#address = ('localhost', 6000)
#conn = Client(address, authkey='secret password')
#conn.send('close')
## can also send arbitrary objects:
## conn.send(['a', 2.5, None, int, sum])
#conn.close()
