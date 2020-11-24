import numpy as np
import cv2
from Model import ModelManusia2
import time
import mysql.connector

# ip = "192.168.100.200"
# port = "554"

class kamera:
    cnt_up = 0
    cnt_down = 0
    count_up = 0
    count_down = 0
    state = 0
    w = 0
    h = 0

    # x1g1 = 0
    # y1g1 = 0
    # x2g1 = 0
    # y2g1 = 0
    # x1g2 = 0
    # y1g2 = 0
    # x2g2 = 0
    # y2g2 = 0

    font = cv2.FONT_HERSHEY_SIMPLEX
    persons = []
    rect_co = []
    max_p_age = 1
    pid = 1
    val = []
#contoh link : "rtsp://admin:cyborg91@192.168.100.200:554/Streaming/Channels/202/"
    def __init__(self,nama_kamera,channel_kamera,x1g1,y1g1,x2g1,y2g1,x1g2,y1g2,x2g2,y2g2):
        self.nama_kamera = nama_kamera
        link = channel_kamera
        self.cap = cv2.VideoCapture()
        print(link)
        self.cap.open(link)


        self.w = self.cap.get(3)
        self.h = self.cap.get(4)
        print(self.h, " ", self.w)
        self.frameArea = self.h * self.w
        self.areaTH = self.frameArea / 300
        self.line_up = int(1 * (self.h / 2))
        self.line_down = int(4 * (self.h / 7))
        self.up_limit = int(.5 * (self.h / 5))
        self.down_limit = int(4.5 * (self.h / 5))
        print("Red line y:", str(self.line_down))
        print("Blue line y:", str(self.line_up))

        # Inisialisasi Garis Batas Penghitung
        self.line_down_color = (255, 0, 0)
        self.line_up_color = (0, 0, 255)
        self.pt1 = [x1g1, y1g1];
        self.pt2 = [x2g1, y2g1];
        self.pts_L1 = np.array([self.pt1, self.pt2], np.int32)
        self.pts_L1 = self.pts_L1.reshape((-1, 1, 2))
        self.pt3 = [x1g2, y1g2];
        self.pt4 = [x2g2, y2g2];
        self.pts_L2 = np.array([self.pt3, self.pt4], np.int32)
        self.pts_L2 = self.pts_L2.reshape((-1, 1, 2))

        # Background Substractor
        self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

        # Inisialisasi Morphographic Filters
        self.kernelOp = np.ones((3, 3), np.uint8)
        self.kernelOp2 = np.ones((5, 5), np.uint8)
        self.kernelCl = np.ones((11, 11), np.uint8)

    def proses(self):
        if (self.cap.isOpened()):
            #print(self.nama_kamera)
            ret, frame = self.cap.read()

            # Modifikasi Background Objek
            fgmask = self.fgbg.apply(frame)
            fgmask2 = self.fgbg.apply(frame)

            # Penghilangan Bayangan Objek
            try:
                ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
                ret, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)
                mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, self.kernelOp)
                mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, self.kernelOp)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernelCl)
                mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, self.kernelCl)
            except:
                print('EOF')
                print('Keluar:', self.cnt_up + self.count_up)
                print('Masuk:', self.cnt_down + self.count_down)
                return

            # Proses Perhitungan
            contours0, hierarchy = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
            for cnt in contours0:
                rect = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)
                if area > self.areaTH: #limitasi area minimal , kalau terlalu kecil di abaikan
                    M = cv2.moments(cnt)
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    x, y, w, h = cv2.boundingRect(cnt)

                    new = True
                    if cy in range(self.up_limit, self.down_limit):
                        for i in self.persons:
                            if abs(cx - i.getX()) <= w and abs(cy - i.getY()) <= h:
                                new = False
                                i.updateCoords(cx, cy)  # update coordinates in the object and resets age
                                if i.going_masuk(self.pt3, self.pt4) == True:
                                    if w > 100:
                                        count_up = w / 60
                                        print
                                    else:
                                        self.cnt_up += 1;
                                    print("ID Objek:", i.getId(), 'Masuk melalui', time.strftime("%c"))
                                elif i.going_DOWN(self.pt1, self.pt2) == True:
                                    if w > 100:
                                        count_down = w / 60
                                    else:
                                        self.cnt_down += 1;
                                    print("ID Objek:", i.getId(), 'Masuk melalui ', time.strftime("%c"))
                                break
                                # if i.going_UP(self.line_down, self.line_up) == True:
                                #     if w > 100:
                                #         count_up = w / 60
                                #         print
                                #     else:
                                #         self.cnt_up += 1;
                                #     print("ID Objek:", i.getId(), 'Masuk melalui', time.strftime("%c"))
                                # elif i.going_DOWN(self.line_down, self.line_up) == True:
                                #     if w > 100:
                                #         count_down = w / 60
                                #     else:
                                #         self.cnt_down += 1;
                                #     print("ID Objek:", i.getId(), 'Masuk melalui ', time.strftime("%c"))
                                # break
                            if i.getState() == '1':
                                if i.getDir() == 'down' and i.getY() > self.down_limit:
                                    i.setDone()
                                elif i.getDir() == 'up' and i.getY() < self.up_limit:
                                    i.setDone()
                            if i.timedOut():
                                index = self.persons.index(i)
                                self.persons.pop(index)
                                del i
                        if new == True:
                            p = ModelManusia2.ManusiaTunggal(self.pid, cx, cy, self.max_p_age)
                            self.persons.append(p)
                            self.pid += 1
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Inisialisasi Monitor
            for i in self.persons:
                cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), self.font, 0.3, i.getRGB(), 1, cv2.LINE_AA)

            str_up = 'KELUAR: ' + str(self.cnt_up)
            str_down = 'MASUK: ' + str(self.cnt_down)
            frame = cv2.polylines(frame, [self.pts_L1], False, self.line_down_color, thickness=2)
            frame = cv2.polylines(frame, [self.pts_L2], False, self.line_up_color, thickness=2)
            # frame = cv2.polylines(frame, [self.pts_L3], False, (255, 255, 255), thickness=1)
            # frame = cv2.polylines(frame, [self.pts_L4], False, (255, 255, 255), thickness=1)
            cv2.putText(frame, str_up, (10, 40), self.font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_up, (10, 40), self.font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), self.font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), self.font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

            # Menampilkan Monitor Penghitung dan Mask
            # cv2.imshow('Monitor Penghitung '+ self.nama_kamera, frame)
            # cv2.imshow('Mask Penghitung ' + self.nama_kamera, mask)
            return frame
            # Listener Untuk Exit Program (Esc)


        def tutup(self):
            # Closing Program
            self.cap.release()
            cv2.destroyAllWindows()

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="db_people_counter_laravel"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT tbl_kameras.id, tbl_kameras.nama_kamera,tbl_kameras.channel_kamera, tbl_kameras.status_reverse, tbl_pengaturangaris.x1g1, tbl_pengaturangaris.y1g1, tbl_pengaturangaris.x2g1, tbl_pengaturangaris.y2g1, tbl_pengaturangaris.x1g2, tbl_pengaturangaris.y1g2, tbl_pengaturangaris.x2g2, tbl_pengaturangaris.y2g2 FROM tbl_kameras INNER JOIN tbl_pengaturangaris ON tbl_kameras.id = tbl_pengaturangaris.id_kamera")

row = mycursor.fetchone()

jumlah_kamera = mycursor.rowcount
nama_kamera = []
channel_kamera = []
#xmax = 576
#ymax = 960
x1g1_arr = []
y1g1_arr = []
x2g1_arr = []
y2g1_arr = []
x1g2_arr = []
y1g2_arr = []
x2g2_arr = []
y2g2_arr = []

while row is not None:
    nama_kamera.append(row[1])
    channel_kamera.append(row[2])
    x1g1_arr.append(row[4])
    y1g1_arr.append(row[5])
    x2g1_arr.append(row[6])
    y2g1_arr.append(row[7])
    x1g2_arr.append(row[8])
    y1g2_arr.append(row[9])
    x2g2_arr.append(row[10])
    y2g2_arr.append(row[11])
    row = mycursor.fetchone()

cam = []
for x in range(jumlah_kamera):
    print(x ," ", y2g2_arr[x])
    cam.append(kamera(nama_kamera[x],channel_kamera[x],x1g1_arr[x],y1g1_arr[x],x2g1_arr[x],y2g1_arr[x],x1g2_arr[x],y1g2_arr[x],x2g2_arr[x],y2g2_arr[x]))


gabungan = 0
while(1):
    gambar = []
    for x in range(jumlah_kamera):
        gambar.append(cam[x].proses())

    i = 0
    batas_baris = 2
    ukuran_lebar = 320
    ukuran_tinggi = 240
    gabungan = 0
    gabungan_utuh = []
    for x in range(jumlah_kamera):
        # cv2.imshow('Monitor Penghitung ' + str(x), gambar[x])
        gambar[x] = cv2.resize(gambar[x],(320,240))
        if (i==0) :
            gabungan = gambar[x]
        else:
            gabungan = np.vstack((gabungan,gambar[x]))

        i+=1
        if i%3==0 :
            gabungan_utuh.append(gabungan)
            gabungan = 0

    if (i%3!=0):
        for j in range(i%3):
            gabungan = np.vstack((gabungan,np.zeros(ukuran_lebar,ukuran_tinggi)))
        gabungan_utuh.append(gabungan)

    i = 0

    for x in range(len(gabungan_utuh)):
        if i==0 :
            gabungan = gabungan_utuh[x]
        else :
            gabungan = np.hstack((gabungan,gabungan_utuh[x]))

    cv2.imshow('frame', gabungan)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break