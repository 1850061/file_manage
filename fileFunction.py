from FCB import FCB
from FAT import FAT
from utils import *
import math
from queue import Queue


def dirAddFile(parentDir, filename, start):
    contentIndex = getContentIndex(parentDir, FAT.nowFat)
    fileContent = readFile()
    alreadyLen = len(contentIndex)
    writeStr = ""
    for i in range(alreadyLen):
        writeStr = writeStr + fileContent[contentIndex[i]]
    writeStr = writeStr.replace('\n', '')
    writeLi = writeStr.split('|')
    writeList = []
    for i in range(len(writeLi) - 1):
        writeList.append(writeLi[i])
    writeList.append(filename + ' ' + str(start))
    writeStr = '|'.join(writeList)
    writeStr = writeStr + '|'
    nowMemLen = math.floor(len(writeStr) / 16 + 1)
    newMenLen = nowMemLen - alreadyLen
    freeBlock = FAT.findFreeBlock(newMenLen)
    if len(freeBlock) != newMenLen:
        return False
    allBlock = contentIndex + freeBlock
    changeFat(allBlock)
    writeContent(writeStr, allBlock)
    return True


def createDir(name, parentDir):
    freeBlock = FAT.findFreeBlock(3)
    changeFat(freeBlock)
    if len(freeBlock) != 3:
        return "磁盘空间不足，创建失败"
    start = freeBlock[0]
    isCreatSuccess = True
    if parentDir != -1:
        isCreatSuccess = dirAddFile(parentDir, name, start)
    if not isCreatSuccess:
        return "磁盘空间不足，创建失败"
    fcbDir = FCB(name, freeBlock[0], 0)
    fcbDir.writeFCB()
    writeIndex = FAT.getBlockIndex(start, 3)
    fileContent = readFile()
    writeStr = toNumDigit(parentDir, 3) + '|' + fileContent[writeIndex][4:]
    fileContent[writeIndex] = writeStr
    with open('fileManage.txt', 'w+') as f:
        f.writelines(fileContent)
    return "创建成功"


def deleteSingleDir(path, start):
    pass


def createTxt(name, start):
    str = createDir(name, start)
    return str


def changeFat(freeBlock):
    for i in range(len(freeBlock) - 1):
        FAT.nowFat[freeBlock[i]] = freeBlock[i + 1]
    FAT.nowFat[freeBlock[len(freeBlock) - 1]] = -1


def showDir(start):
    dirName = findDirFile(start, FAT.nowFat)['name']
    list = []
    for i in range(len(dirName)):
        list.append(dirName[i])
    return list


def openDirUnderNow(start, name):
    if name.endswith('.txt'):
        return '请输入目录名，而非文件名'
    fileNames = findDirFile(start, FAT.nowFat)['name']
    fileBlock = findDirFile(start, FAT.nowFat)['block']
    for i in range(len(fileNames)):
        if fileNames[i] == name:
            return fileBlock[i]
    return '没找到该目录'


def openFileUnderNow(start, name):
    fileNames = findDirFile(start, FAT.nowFat)['name']
    fileBlock = findDirFile(start, FAT.nowFat)['block']
    for i in range(len(fileNames)):
        if fileNames[i] == name:
            return fileBlock[i]
    return '没找到该文件'


def openDir(start, path):
    list = path.split('/')
    now = start
    if list[0] == 'root:':
        now = 52
        list = list[1:]
    for i in range(len(list)):
        if list[i] == '.':
            continue
        elif list[i] == '..':
            par = getParDirBlock(now, FAT.nowFat)
            if par == -1:
                return '您已经在根目录，无法回退'
            now = par
        elif list[i] == '':
            continue
        else:
            res = openDirUnderNow(now, list[i])
            if len(str(res)) > 3:
                return res
            now = res
    return now


def rename(origin, new, nowBlock):
    contentIndex = getContentIndex(nowBlock, FAT.nowFat)
    alreadyLen = len(contentIndex)
    writeStr = findDirStr(nowBlock, FAT.nowFat)
    writeStr = writeStr.replace(origin, new)
    nowMemLen = math.floor(len(writeStr) / 16 + 1)
    newMenLen = nowMemLen - alreadyLen
    if newMenLen >= 0:
        freeBlock = FAT.findFreeBlock(newMenLen)
        if len(freeBlock) != newMenLen:
            return '重命名失败，（磁盘空间不足）'
        allBlock = contentIndex + freeBlock
        changeFat(allBlock)
        writeContent(writeStr, allBlock)
    else:
        dec = alreadyLen - nowMemLen
        clearFat(contentIndex[-dec - 1:])
        contentIndex = contentIndex[0: -dec]
        writeContent(writeStr, contentIndex)
    fileIndex = int(openFileUnderNow(nowBlock, new))
    fcbInfo = getFCBInfo(fileIndex, FAT.nowFat)
    fcb = FCB(new, fcbInfo['start'], fcbInfo['size'])
    fcb.writeFCB()
    return '重命名成功'


def eraseFat(list):
    for i in range(len(list)):
        FAT.nowFat[list[i]] = -2


def clearFat(list):
    for i in range(len(list)):
        if i == 0:
            FAT.nowFat[list[i]] = -1
            continue
        else:
            FAT.nowFat[list[i]] = -2


def readTxt(nowBlock, name):
    fileIndex = openFileUnderNow(nowBlock, name)
    if fileIndex == '没找到该文件':
        return fileIndex
    fileIndex = int(fileIndex)
    content = findDirStr(fileIndex, FAT.nowFat)[4:-1]
    return content


def closeFile(nowBlock):
    return


def writeTxt(nowBlock, name, content):
    fileIndex = openFileUnderNow(nowBlock, name)
    if fileIndex == '没找到该文件':
        return fileIndex
    content = content + '|'
    fileIndex = int(fileIndex)
    contentIndex = getContentIndex(fileIndex, FAT.nowFat)
    alreadyLen = len(contentIndex)
    head = findDirStr(nowBlock, FAT.nowFat)[0:4]
    writeStr = findDirStr(nowBlock, FAT.nowFat)[4:-1]
    writeStr = head + writeStr.replace(writeStr, content)
    nowMemLen = math.floor(len(writeStr) / 16 + 1)
    newMenLen = nowMemLen - alreadyLen
    if newMenLen >= 0:
        freeBlock = FAT.findFreeBlock(newMenLen)
        if len(freeBlock) != newMenLen:
            return '重命名失败，（磁盘空间不足）'
        allBlock = contentIndex + freeBlock
        changeFat(allBlock)
        writeContent(writeStr, allBlock)
    else:
        dec = alreadyLen - nowMemLen
        clearFat(contentIndex[-dec - 1:])
        contentIndex = contentIndex[0: -dec]
        writeContent(writeStr, contentIndex)
    fcbInfo = getFCBInfo(fileIndex, FAT.nowFat)
    fcb = FCB(name, fcbInfo['start'], len(content))
    fcb.writeFCB()
    return '写入成功'


def seeTxt(nowBlock, name):
    fileIndex = openFileUnderNow(nowBlock, name)
    if fileIndex == '没找到该文件':
        return fileIndex
    fileIndex = int(fileIndex)
    fcbInfo = getFCBInfo(fileIndex, FAT.nowFat)
    return fcbInfo


def dirDeleteFile(parentDir, filename):
    contentIndex = getContentIndex(parentDir, FAT.nowFat)
    fileContent = readFile()
    alreadyLen = len(contentIndex)
    writeStr = ""
    for i in range(alreadyLen):
        writeStr = writeStr + fileContent[contentIndex[i]]
    writeStr = writeStr.replace('\n', '')
    writeLi = writeStr.split('|')
    writeList = []
    for i in range(len(writeLi) - 1):
        name = writeLi[i].split(' ')[0]
        if name == filename:
            continue
        writeList.append(writeLi[i])
    writeStr = '|'.join(writeList)
    writeStr = writeStr + '|'
    nowMemLen = math.floor(len(writeStr) / 16 + 1)
    newMenLen = nowMemLen - alreadyLen
    if newMenLen >= 0:
        freeBlock = FAT.findFreeBlock(newMenLen)
        if len(freeBlock) != newMenLen:
            return '重命名失败，（磁盘空间不足）'
        allBlock = contentIndex + freeBlock
        changeFat(allBlock)
        writeContent(writeStr, allBlock)
    else:
        dec = alreadyLen - nowMemLen
        clearFat(contentIndex[-dec - 1:])
        contentIndex = contentIndex[0: -dec]
        writeContent(writeStr, contentIndex)
    return True


def deleteSingleFile(nowBlock, name):
    fileIndex = openFileUnderNow(nowBlock, name)
    fileIndex = int(fileIndex)
    list = getFileIndex(fileIndex, FAT.nowFat)
    eraseFat(list)


def deleteFileByBlock(fileIndex):
    list = getFileIndex(fileIndex, FAT.nowFat)
    eraseFat(list)


def deleteFile(nowBlock, name):
    fileIndex = openFileUnderNow(nowBlock, name)
    if fileIndex == '没找到该文件':
        return fileIndex
    fileIndex = int(fileIndex)
    deleteList = findDirFile(fileIndex, FAT.nowFat)['block']
    deleteQueue = Queue(maxsize=0)
    for i in range(len(deleteList)):
        if deleteList[i] == '':
            continue
        deleteQueue.put(int(deleteList[i]))
    while not deleteQueue.empty():
        now = deleteQueue.get()
        if getFileType(now, FAT.nowFat) == '目录':
            deleteList = findDirFile(now, FAT.nowFat)['block']
            for i in range(len(deleteList)):
                if deleteList[i] == '':
                    continue
                deleteQueue.put(int(deleteList[i]))
            deleteFileByBlock(now)
        else:
            deleteFileByBlock(now)
    deleteSingleFile(nowBlock, name)
    dirDeleteFile(nowBlock, name)
    return '删除成功'
