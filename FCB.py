import time
from utils import *
from FAT import FAT


# 文件控制块
class FCB:
    def __init__(self, name, start, size):
        self.name = name
        self.start = start
        # 文件类型，文件夹为0，文本文件为1
        if len(name) > 4 and name[-4:] == '.txt':
            self.type = 1
        else:
            self.type = 0
        self.lastModify = time.localtime()
        self.size = size

    # 把FCB写入磁盘
    def writeFCB(self):
        fileContent = readFile()
        writeStr = toNumDigit(self.name, 10) + toNumDigit(self.start, 3) + toNumDigit(self.size, 3) + '\n'
        fileContent[self.start] = writeStr
        writeStr = str(self.type) + str(self.lastModify.tm_year) + str(toNumDigit(self.lastModify.tm_mon, 2)) + \
                   str(toNumDigit(self.lastModify.tm_mday, 2)) + str(toNumDigit(self.lastModify.tm_hour, 2)) + \
                   str(toNumDigit(self.lastModify.tm_min, 2)) + str(toNumDigit(self.lastModify.tm_sec, 2)) + '0\n'
        fat = FAT.nowFat
        nextIndex = fat[self.start]
        fileContent[nextIndex] = writeStr
        with open('fileManage.txt', 'w') as f:
            f.writelines(fileContent)
