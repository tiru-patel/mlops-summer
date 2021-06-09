import os 
import cv2 
cap=cv2.VideoCapture(1)
import numpy as np
import socket 

# Create Socket
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip="192.168.43.174"
port=8888
# Socket Binding
s.bind((ip,port))

s.listen(5)
# Listening and waiting for connection
conn,addr = s.accept()

while True: 
    data = conn.recv(90456)
    # Decode the image
    arry = np.fromstring(data, np.uint8)
    photo = cv2.imdecode(arry, cv2.IMREAD_COLOR)
    if type(photo) is type(None):
        pass
    else:
        cv2.imshow("SERVER-SCREEN",photo)
        if cv2.waitKey(10)==13:
            break
    stat,photo=cap.read()
    # Encode image and send via network
    photo_data = cv2.imencode('.jpg', photo)[1].tobytes()
    conn.sendall(photo_data)
cv2.destroyAllWindows()
cap.release()
os.system("cls")