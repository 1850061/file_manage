# 0-51号块存FAT，第52号块存root
from utils import *


class FAT:
    nowFat = None

    def __init__(self, isIni):
        if isIni:
            self.FAT = [-2] * 256
            for i in range(52):
                self.FAT[i] = -1
            FAT.nowFat = self.FAT
        else:
            self.FAT = [-2] * 256
            self.loadFAT()
            FAT.nowFat = self.FAT

    # 获取FAT
    def loadFAT(self):
        fatIndex = 0
        isContinue = True
        with open('fileManage.txt', 'r') as f:
            for line in f.readlines():
                for i in range(5):
                    str = line[3 * i: 3 * i + 3]
                    if str == '000':
                        self.FAT[fatIndex] = 0
                    else:
                        isFirst = True
                        countZero = 0
                        for i in range(len(str)):
                            if str[i] == '0' and isFirst:
                                countZero += 1
                            else:
                                isFirst = False
                        if str[len(str) - 1] == '\n':
                            self.FAT[fatIndex] = int(str[countZero:-1])
                        else:
                            self.FAT[fatIndex] = int(str[countZero:])
                    fatIndex += 1
                    if fatIndex == 256:
                        isContinue = False
                        break
                if not isContinue:
                    break

    @classmethod
    # 把FAT写入磁盘
    def writeFAT(cls):
        fileContent = readFile()
        writeStr = ""
        fileIndex = 0
        for i in range(len(cls.nowFat)):
            if i % 5 == 0 and i != 0:
                writeStr += '0\n'
                fileContent[fileIndex] = writeStr
                fileIndex = fileIndex + 1
                writeStr = ""
            writeStr = writeStr + toNumDigit(cls.nowFat[i], 3)
        fileContentInstead(fileContent, fileIndex, 0, 3, writeStr)

        with open('fileManage.txt', 'w') as f:
            f.writelines(fileContent)

    @classmethod
    def findFreeBlock(cls, num):
        threeFree = []
        for i in range(256):
            if len(threeFree) >= num:
                break
            if cls.nowFat[i] == -2:
                threeFree.append(i)
        return threeFree

    @classmethod
    def getBlockIndex(cls, start, num):
        if num == 1:
            return start
        nowBlock = start
        for i in range(num - 1):
            if nowBlock == -1:
                return -1
            nowBlock = cls.nowFat[nowBlock]
        return nowBlock
