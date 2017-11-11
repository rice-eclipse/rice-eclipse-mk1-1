import socket
import time
def Main():
    host="127.0.0.1"
    port=1234
    s=socket.socket()
    s.bind((host,port))

    s.listen(1)
    C,addr=s.accept()
    i=0
    timestamp=0
    while True:
        # data=C.recv(1024)
        # data=data.decode()
        # if not data:
        #     break
        # print ("from client"+str(data))
        # data=str(data).upper()
        #
        # print("sending"+str(data))
        C.send(i.to_bytes(2, byteorder='big'))
        C.send(timestamp.to_bytes(8,byteorder='big'))
        i=(i+1)% 1000
        timestamp=timestamp+1
        time.sleep(0.00005)

    C.close()


if __name__=='__main__':
    Main()