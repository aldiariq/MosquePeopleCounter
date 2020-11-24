from random import randint

class ManusiaTunggal:
    tracks = []

    def __init__(self, i, xi, yi, max_age):
        self.i = i
        self.x = xi
        self.y = yi
        self.tracks = []
        self.R = randint(0, 255)
        self.G = randint(0, 255)
        self.B = randint(0, 255)
        self.done = False
        self.state = '0'
        self.age = 0
        self.max_age = max_age
        self.dir = None

    def getRGB(self):
        return (self.R, self.G, self.B)

    def getTracks(self):
        return self.tracks

    def getId(self):
        return self.i

    def getState(self):
        return self.state

    def getDir(self):
        return self.dir

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def updateCoords(self, xn, yn):
        self.age = 0
        self.tracks.append([self.x, self.y])
        self.x = xn
        self.y = yn

    def setDone(self):
        self.done = True

    def timedOut(self):
        return self.done



    def directionOfPoint(self,titik1, titik2, titik_dicari):
        titik1[1] = -titik1[1];
        titik2[1] = -titik2[1];
        titik_dicari[1] = -titik_dicari[1];
        # Subtracting co-ordinates of
        # point A from B and P, to
        # make A as origin
        titik2[0] -= titik1[0]
        titik2[1] -= titik1[1]
        titik_dicari[0] -= titik1[0]
        titik_dicari[1] -= titik1[1]

        # Determining cross Product
        cross_product = titik2[0] * titik_dicari[1] - titik2[1] * titik_dicari[0]

        # Return RIGHT if cross product is positive
        if (cross_product > 0):
            return 1

        # Return LEFT if cross product is negative
        if (cross_product < 0):
            return -1

        # Return ZERO if cross product is zero
        return 0
    # asumsi kanan adalah titik di mana dia bertambah/masuk
    def going_masuk(self, titik_awal_kanan, titik_akhir_kanan):
        if len(self.tracks) >= 2: #minimal ada 2 track
            if self.state == '0':
                #ini untuk mengecek apakah orang bergerak dari bawah ke atas
                #remember ke atas semakin kecil angkanya
                if (self.directionOfPoint(titik_awal_kanan,titik_akhir_kanan,self.tracks[-1]) == 1 and \
                        self.directionOfPoint(titik_awal_kanan,titik_akhir_kanan,self.tracks[-2]) <= 0) :  # cruzo la linea
                    state = '1'
                    self.dir = 'up'
                    return True
            else:
                return False
        else:
            return False

    def going_keluar(self, titik_awal_kiri, titik_akhir_kiri):
        if len(self.tracks) >= 2: #minimal ada 2 track
            if self.state == '0':
                #ini untuk mengecek apakah orang bergerak dari atas ke bawah
                #remember ke atas semakin kecil angkanya
                if (self.directionOfPoint(titik_awal_kiri,titik_akhir_kiri,self.tracks[-1]) == -1 and \
                        self.directionOfPoint(titik_awal_kiri,titik_akhir_kiri,self.tracks[-2]) >= 0) :  # cruzo la linea
                    state = '1'
                    self.dir = 'down'
                    return True
            else:
                return False
        else:
            return False

    def going_UP(self, mid_start, mid_end):
        if len(self.tracks) >= 2: #minimal ada 2 track
            if self.state == '0':
                #ini untuk mengecek apakah orang bergerak dari bawah ke atas
                #remember ke atas semakin kecil angkanya
                if self.tracks[-1][1] < mid_end and self.tracks[-2][1] >= mid_end:  # cruzo la linea
                    state = '1'
                    self.dir = 'up'
                    return True
            else:
                return False
        else:
            return False

    def going_DOWN(self, mid_start, mid_end):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] > mid_start and self.tracks[-2][1] <= mid_start:  # cruzo la linea
                    state = '1'
                    self.dir = 'down'
                    return True
            else:
                return False
        else:
            return False

    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True


class ManusiaJamak:
    def __init__(self, persons, xi, yi):
        self.persons = persons
        self.x = xi
        self.y = yi
        self.tracks = []
        self.R = randint(0, 255)
        self.G = randint(0, 255)
        self.B = randint(0, 255)
        self.done = False
