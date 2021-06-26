def readFile():
    fileContent = []
    with open('fileManage.txt', 'r') as f:
        for line in f.readlines():
            fileContent.append(line)
    return fileContent


def toNumDigit(num, all):
    addZero = all - len(str(num))
    return '0' * addZero + str(num)


def eliminateZero(name):
    isFirst = True
    countZero = 0
    for i in range(len(name)):
        if name[i] == '0' and isFirst:
            countZero += 1
        else:
            isFirst = False
    if name[countZero:] != '':
        return name[countZero:]
    else:
        return '0'


def fileContentInstead(list, index, begin, length, replaceStr):
    list[index] = list[index][0:begin] + replaceStr + list[index][begin + length:]


def checkFile(name, start, size):
    if 'root:' == name:
        return '文件创建失败（文件命名不能与根目录重名）'
    for i in range(len(name)):
        if name[i] == '0' or name[i] == '|' or name[i] == '/':
            return "文件创建失败（文件名中不能包含0，|以及/符号）"
        else:
            break
    for ch in name.encode('utf-8').decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return "文件创建失败（文件名中不能包含中文）"
    if len(name) > 10:
        return "文件创建失败（文件名长度不能超过10）"
    if int(start) >= 256:
        return "文件创建失败（起始地址错误）"
    if size >= 1000:
        return "文件创建失败（文件过大）"
    return "Success"


def containChinese(content):
    for ch in content.encode('utf-8').decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def checkDir(name, start, fat):
    if 'root:' == name:
        return '目录命名失败（文件命名不能与根目录重名）'
    if name.endswith('.txt'):
        return '目录命名错误（不能以.txt结尾）'
    if len(name) == 0:
        return '目录命名错误（目录名不能为空）'
    dirInfo = findDirFile(start, fat)
    dirNames = dirInfo['name']
    for i in range(len(dirNames)):
        if name == dirNames[i]:
            return '目录命名错误（目录名不允许重名）'
    return 'Success'


def getFCBIndex(start, fat):
    return [start, fat[start]]


def getFCBInfo(start, fat):
    fileContent = readFile()
    info = fileContent[start]
    sec = fat[start]
    time = fileContent[sec]
    type = ''
    if time[0] == '0':
        type = '目录'
    else:
        type = 'Txt文件'
    t = time[1:5] + '-' + time[5:7] + '-' + time[7:9] + ' ' + time[9:11] + '-' + time[11:13] + '-' + time[13:15] + ' '
    return {'name': eliminateZero(info[0:10]), 'start': int(eliminateZero(info[10:13])),
            'size': int(eliminateZero(info[13:16])), 'type': type, 'lastModifyTime': t}


def getFileType(startBlock, fat):
    info = getFCBInfo(startBlock, fat)
    return info['type']


# 获取内容的编号
def getContentIndex(start, fat):
    index = []
    now = fat[fat[start]]
    while now != -1:
        index.append(now)
        now = fat[now]
    return index


def getFileIndex(start, fat):
    return getFCBIndex(start, fat) + getContentIndex(start, fat)


def writeContent(str, blockList):
    fileContent = readFile()
    for i in range(len(blockList) - 1):
        fileContent[blockList[i]] = str[16 * i: 16 * i + 16] + '\n'
    lastLen = len(str) % 16
    fileContent[blockList[len(blockList) - 1]] = str[-lastLen:] + "0" * (16 - lastLen) + '\n'
    with open('fileManage.txt', 'w') as f:
        f.writelines(fileContent)


def getParDirBlock(start, fat):
    fileContent = readFile()
    par = fileContent[getContentIndex(start, fat)[0]][0:3]
    res = 0
    if par == '000':
        res = 0
    else:
        isFirst = True
        countZero = 0
        for i in range(len(par)):
            if par[i] == '0' and isFirst:
                countZero += 1
            else:
                isFirst = False
        res = int(par[countZero:])
    return res


def findDirFile(start, fat):
    contentIndex = getContentIndex(start, fat)
    fileContent = readFile()
    alreadyLen = len(contentIndex)
    writeStr = ""
    for i in range(alreadyLen):
        writeStr = writeStr + fileContent[contentIndex[i]]
    writeStr = writeStr.replace('\n', '')
    writeLi = writeStr.split('|')
    writeList = []
    for i in range(len(writeLi) - 1):
        if i == 0:
            continue
        writeList.append(writeLi[i])
    name = []
    block = []
    for i in range(len(writeList)):
        temp = writeList[i].split(' ')
        name.append(temp[0])
        block.append(temp[1])
    return {'name': name, 'block': block}


def findDirStr(start, fat):
    contentIndex = getContentIndex(start, fat)
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
    writeStr = '|'.join(writeList)
    writeStr = writeStr + '|'
    return writeStr


def canRename(origin, new, start, fat):
    res = checkFile(new, start, 0)
    res = res.replace('创建', '重命名')
    if res == 'Success':
        pass
    else:
        return res
    if 'root:' == new:
        return '重命名失败（文件命名不能与根目录重名）'
    isDirOri = True
    isDirNew = True
    if origin.endswith('.txt'):
        isDirOri = False
    if new.endswith('.txt'):
        isDirNew = False
    if isDirOri != isDirNew:
        return '重命名失败（重命名不能改变文件类型）'
    names = findDirFile(start, fat)['name']
    isAppear = False
    for i in range(len(names)):
        if new == names[i]:
            return '重命名失败（以该文件名命名得文件已存在）'
        if origin == names[i]:
            isAppear = True
    if isAppear:
        return 'Success'
    return '重命名失败（该文件不存在）'


def checkPath(path):
    for i in range(len(path)):
        if path[i] == '\\':
            return 'path中不应该出现\\符号'
    return 'Success'


def combinePath(nowPath, addPath):
    res = []
    now = nowPath.split('/')
    add = addPath.split('/')
    if add[0] == 'root:':
        if addPath.endswith('/'):
            return addPath
        return addPath + '/'
    for i in range(len(add)):
        if add[len(add) - i - 1] == '.':
            del add[len(add) - i - 1]
    back = 1
    for i in range(len(add)):
        if add[i] == '..':
            back = back + 1
    res = res + now[0: -back]
    res = res + add[back - 1:]
    path = '/'.join(res)
    if path.endswith('/'):
        return path
    return path + '/'
