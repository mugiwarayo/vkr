import socket
import struct
import os
from yolov5.detect import run
import wmi


model = 'model/last.pt'

def receive_file_size(sck: socket.socket):
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()
    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    filesize = struct.unpack(fmt, stream)[0]
    return filesize


def receive_file(sck: socket.socket, filename):
    filesize = receive_file_size(sck)
    with open(filename, "wb") as f:
        received_bytes = 0
        while received_bytes < filesize:
            chunk = sck.recv(1024)
            if chunk:
                f.write(chunk)
                received_bytes += len(chunk)

def check(arr):
    if '0' or '1' in arr:
        return False
    if arr.count('2') != 1:
        return False
    return True

obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)
displays = [x for x in obj if 'DISPLAY' in str(x)]
counter = 0

if len(displays) == 1:

    with socket.create_server(( "localhost", 6190)) as server:
        print("Ожидание клиента...")
        conn, address = server.accept()
        print(f"{address[0]}:{address[1]} подключен.")
        print("Получаем файл...")
        while True:
            receive_file(conn, f"images/image-received{counter}.png")
            pred = run(weights=model, source=f'images/image-received{counter}.png',
                       imgsz=[416, 416], save_txt=True, conf_thres=0.1, iou_thres=0.65)
            if counter == 0:
                if len(os.listdir('yolov5/runs/detect/exp/labels')) != 0:
                    with open('yolov5/runs/detect/exp/labels/image-received0.txt', 'r') as file:
                        lines = file.readlines()
                        arr = []
                        for line in lines:
                            arr.append(line.split()[0])
                        if not check(arr):
                            os.replace(f'yolov5/runs/detect/exp{counter + 1}/image-received{counter}.png', 'suspect/')
            else:
                if len(os.listdir(f'yolov5/runs/detect/exp/labels')) != 0:
                    with open(f'yolov5/runs/detect/exp{counter + 1}/labels/image-received{counter}.txt', 'r') as file:
                        lines = file.readlines()
                        arr = []
                        for line in lines:
                            arr.append(line.split()[0])
                        if not check(arr):
                            os.replace(f'yolov5/runs/detect/exp{counter + 1}/image-received{counter}.png', 'suspect/')


            counter += 1
            print("Файл получен.")
    print("Соединение закрыто.")
else:
    print('У пользователя больше 2 мониторов.')