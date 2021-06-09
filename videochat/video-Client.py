import os
import cv2 
cap=cv2.VideoCapture(0)
import numpy as np
import socket 

# Client socket created
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip="192.168.43.174"
port=8888
# Connection to server 
s.connect((ip,port))

while True: 
    stat,photo=cap.read()
    # Encode and send data via network
    photo_data = cv2.imencode('.jpg', photo)[1].tobytes()
    s.sendall(photo_data)
    
    data = s.recv(90456)
    # Decode the image
    arry = np.fromstring(data, np.uint8)
    photo = cv2.imdecode(arry, cv2.IMREAD_COLOR)
    if type(photo) is type(None):
        pass
    else:
        cv2.imshow("CLIENT-SCREEN",photo)
        if cv2.waitKey(10)==13:
            break
cv2.destroyAllWindows()
cap.release()
os.system("cls")