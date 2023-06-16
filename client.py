import os
import socket
import struct
import time
import cv2 as cv
from tkinter import *
from tkinter import messagebox


class MainApp:
    def __init__(self):
        self.root = Tk()
        self.root.title('Прокторинг')
        self.root.geometry('500x150')
        self.root.resizable(False, False)
        self.set_widgets()

    def set_widgets(self):
        Label(self.root, text='Добро пожаловать в систему прокторинга', font=15).pack()
        Button(text='Подключиться к экзамену', command=self.video, width=20).pack()
        Button(text='Проверить камеру', command=self.camera_check, width=20).pack()
        Button(text='Выйти', command=self.exit, width=20).pack(side=BOTTOM)

    def exit(self):
        self.root.destroy()

    @staticmethod
    def camera_check():
        camera_check = CameraCheck()

    @staticmethod
    def send_file(sck: socket.socket, filename):
        filesize = os.path.getsize(filename)
        sck.sendall(struct.pack("<Q", filesize))
        with open(filename, "rb") as f:
            while read_bytes := f.read(1024):
                sck.sendall(read_bytes)

    def video(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            messagebox.showerror('Ошибка', 'Отсутствует камера!')
            exit()

        with socket.create_connection(("localhost", 6190)) as conn:
            t = time.time()
            while True:
                ret, frame = self.cap.read()
                if frame is not None:
                    # if frame is read correctly ret is True
                    if not ret:
                        print("Can't receive frame (stream end?). Exiting ...")
                        break

                    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                    cv.putText(frame, 'Exam',
                               (0, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv.imshow('frame', frame)
                    if time.time() - t >= 3.0:
                        print("Подключение к серверу.")
                        print("Передача файла...")
                        resized_frame = cv.resize(gray, (416, 416))
                        cv.imwrite('images/image.png', resized_frame)
                        self.send_file(conn, f"images/image.png")
                        print("Отправлено.")
                        t = time.time()

                    if cv.waitKey(1) == ord('q'):
                        break

        self.cap.release()
        cv.destroyAllWindows()

    def start_app(self):
        self.root.mainloop()


class CameraCheck:
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            messagebox.showerror('Ошибка', 'Отсутствует камера!')
            exit()
        self.video()

    def video(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()

        while True:
            ret, frame = self.cap.read()
            if frame is not None:
                # if frame is read correctly ret is True
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
                cv.putText(frame, 'Camera checking',
                           (0, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv.putText(frame, 'Press Q to stop',
                           (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv.imshow('Checking the camera', frame)

                if cv.waitKey(1) == ord('q'):
                    break
        self.cap.release()
        cv.destroyAllWindows()


app = MainApp()
app.start_app()
