import numpy as np
import cv2
from Model import ModelManusia
import time
import datetime
import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="",
  database="db_people_counter_laravel"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT tbl_kameras.id, tbl_kameras.nama_kamera,tbl_kameras.channel_kamera, tbl_kameras.status_reverse, tbl_pengaturangaris.x1g1, tbl_pengaturangaris.y1g1, tbl_pengaturangaris.x2g1, tbl_pengaturangaris.y2g1, tbl_pengaturangaris.x1g2, tbl_pengaturangaris.y1g2, tbl_pengaturangaris.x2g2, tbl_pengaturangaris.y2g2 FROM tbl_kameras INNER JOIN tbl_pengaturangaris ON tbl_kameras.id = tbl_pengaturangaris.id_kamera")

row = mycursor.fetchone()

while row is not None:
    print(row)
    row = mycursor.fetchone()

print("A" + cv2.__version__);

cnt_up = 0
cnt_down = 0
count_up = 0
count_down = 0
state = 0

cap = cv2.VideoCapture(0)
# Resolusi Kamera : 720x480

for i in range(19):
    print(i), cap.get(i)

w = cap.get(3)
h = cap.get(4)
frameArea = h * w
areaTH = frameArea / 300

# Inisialisasi Garis Batas Penghitung
line_up = int(1 * (h / 2))
line_down = int(4 * (h / 7))

up_limit = int(.5 * (h / 5))
down_limit = int(4.5 * (h / 5))

print("Red line y:"), str(line_down)
print("Blue line y:"), str(line_up)
line_down_color = (255, 0, 0)
line_up_color = (0, 0, 255)
#       x   y
pt1 = [0, line_down];
pt2 = [w, line_down];
pts_L1 = np.array([pt1, pt2], np.int32)
pts_L1 = pts_L1.reshape((-1, 1, 2))

pt3 = [0, line_up];
pt4 = [w, line_up];
pts_L2 = np.array([pt3, pt4], np.int32)
pts_L2 = pts_L2.reshape((-1, 1, 2))

pt5 =  [0, up_limit];
pt6 =  [w, up_limit];
pts_L3 = np.array([pt5, pt6], np.int32)
pts_L3 = pts_L3.reshape((-1, 1, 2))
pt7 = [0, down_limit];
pt8 = [w, down_limit];
pts_L4 = np.array([pt7, pt8], np.int32)
pts_L4 = pts_L4.reshape((-1, 1, 2))

# Background Substractor
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

# Inisialisasi Morphographic Filters
kernelOp = np.ones((3, 3), np.uint8)
kernelOp2 = np.ones((5, 5), np.uint8)
kernelCl = np.ones((11, 11), np.uint8)

# Inisialisasi Variabel
font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
rect_co = []
max_p_age = 1
pid = 1
val = []

while (cap.isOpened()):
    ret, frame = cap.read()

    # Modifikasi Background Objek
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

    # Penghilangan Bayangan Objek
    try:
        ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        ret, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print('Keluar:'), cnt_up + count_up
        print('Masuk:'), cnt_down + count_down
        break

    # Proses Perhitungan
    contours0, hierarchy = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        rect = cv2.boundingRect(cnt)

        area = cv2.contourArea(cnt)
        if area > areaTH:
            M = cv2.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            x, y, w, h = cv2.boundingRect(cnt)

            new = True
            if cy in range(up_limit, down_limit):
                for i in persons:
                    if abs(cx - i.getX()) <= w and abs(cy - i.getY()) <= h:
                        new = False
                        i.updateCoords(cx, cy)  # update coordinates in the object and resets age
                        if i.going_UP(line_down, line_up) == True:
                            if w > 100:
                                count_up = w / 60
                                print
                            else:
                                cnt_up += 1;
                                sql = "DELETE FROM tbl_pengunjungs WHERE id=(SELECT MAX(id) FROM tbl_pengunjungs)"
                                mycursor.execute(sql)

                                mydb.commit()
                            print("ID Objek:", i.getId(), 'Masuk melalui', time.strftime("%c"))
                        elif i.going_DOWN(line_down, line_up) == True:
                            if w > 100:
                                count_down = w / 60
                            else:
                                cnt_down += 1;

                                sql = "INSERT INTO tbl_pengunjungs (id_kamera, status, created_at, updated_at) VALUES (%s, %s, %s, %s)"
                                val = (1, 1, datetime.datetime.now(), datetime.datetime.now())
                                mycursor.execute(sql, val)

                                mydb.commit()
                            print("ID Objek:", i.getId(), 'Masuk melalui ', time.strftime("%c"))
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        index = persons.index(i)
                        persons.pop(index)
                        del i
                if new == True:
                    p = ModelManusia.ManusiaTunggal(pid, cx, cy, max_p_age)
                    persons.append(p)
                    pid += 1
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Inisialisasi Monitor
    for i in persons:
        cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)
    str_up = 'KELUAR: ' + str(round(cnt_up))
    str_down = 'MASUK: ' + str(round(cnt_down))


    frame = cv2.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
    frame = cv2.polylines(frame, [pts_L2], False, line_up_color, thickness=2)
    frame = cv2.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
    frame = cv2.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
    cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    # Menampilkan Monitor Penghitung dan Mask
    cv2.imshow('Monitor Penghitung', frame)
    # cv2.imshow('Mask Penghitung',mask)

    # Listener Untuk Exit Program (Esc)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        # sql = "DELETE FROM tbl_pengunjungs"
        # mycursor.execute(sql)
        #
        # mydb.commit()
        break

# Closing Program
cap.release()
cv2.destroyAllWindows()