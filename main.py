# 共256个内存块，每个16Byte
import os
from FAT import FAT
from fileFunction import *

nowFat = None
nowBlock = 52
pathNow = 'root:/'
help = []


def iniFile():
    global nowFat
    if os.path.exists('fileManage.txt'):
        nowFat = FAT(False)
    else:
        reset()
    with open('help.txt', 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            help.append(line)


def printHelp():
    global help
    for line in help:
        print(line, end='')
    print('以上为本文件系统所提供的指令')


def reset():
    global nowFat
    with open('fileManage.txt', 'w+') as f:
        writeList = [""] * 256
        for i in range(256):
            writeList[i] = "0" * 16 + "\n"
        f.writelines(writeList)
    nowFat = FAT(True)
    createDir('root', -1)


def fileController():
    global nowBlock, pathNow
    print('欢迎进入文件管理系统，你可以输入help获取帮助')
    print('本文件管理系统中，磁盘一共256块，每块大小16Byte')
    while True:
        print(pathNow + '>', end='')
        command = input()
        # 退出
        if command == 'exit':
            FAT.writeFAT()
            break
        # 操作提示
        elif command == 'help':
            printHelp()
        # 创建目录
        elif command.startswith('create dir '):
            name = command.split(' ')[2]
            res = checkFile(name, nowBlock, 1)
            if res != 'Success':
                print(res)
                continue
            res = checkDir(name, nowBlock, FAT.nowFat)
            if res == 'Success':
                strr = createDir(name, nowBlock)
                print(strr)
            else:
                print(res)
        # 展示目录
        elif command == 'show dir':
            print(showDir(nowBlock))
        # 创建文件
        elif command.startswith('create txt '):
            name = command.split(' ')[2]
            if not name.endswith('.txt'):
                print('请创建txt文件')
                continue
            res = checkFile(name, nowBlock, 1)
            if res != 'Success':
                print(res)
                continue
            strr = createTxt(name, nowBlock)
            print(strr)
        # cd功能
        elif command.startswith('cd '):
            path = command.split(' ')[1]
            res = checkPath(path)
            if res != 'Success':
                print(res)
                continue
            res = openDir(nowBlock, path)
            if len(str(res)) > 3:
                print(res)
                continue
            nowBlock = int(res)
            pathNow = combinePath(pathNow, path)
        # 格式化文件
        elif command == 'reset':
            reset()
            nowBlock = 52
            pathNow = 'root:/'
            print('格式化已完成')
        # 文件重命名
        elif command.startswith('rename '):
            if len(command.split(' ')) < 3:
                print('输入错误，请输入command help查看指令')
                continue
            origin = command.split(' ')[1]
            new = command.split(' ')[2]
            res = canRename(origin, new, nowBlock, FAT.nowFat)
            if res != 'Success':
                print(res)
                continue
            res = rename(origin, new, nowBlock)
            print(res)
        # 读文件
        elif command.startswith('read txt '):
            name = command.split(' ')[2]
            if not name.endswith('.txt'):
                print('只允许读.txt文件')
                continue
            res = readTxt(nowBlock, name)
            if res == '没找到该文件':
                print(res)
                continue
            print('读取成功，内容为:', end='')
            if res == '':
                res = '空'
            print(res)
        # 写文件
        elif command.startswith('write txt '):
            if len(command.split(' ')) < 3:
                print('输入错误，请输入command help查看指令')
                continue
            name = command.split(' ')[2]
            content = command.split(' ')[3]
            if not name.endswith('.txt'):
                print('只允许写.txt文件')
                continue
            if len(content) >= 1000:
                print('只允许写入小于1000个字符的内容')
                continue
            if containChinese(content):
                print('输入内容不允许出现中文')
                continue
            res = writeTxt(nowBlock, name, content)
            if res == '没找到该文件':
                print(res)
                continue
            print(res)
        # 查看文件属性
        elif command.startswith('see txt '):
            name = command.split(' ')[2]
            if not name.endswith('.txt'):
                print('只允许查看以.txt文件')
                continue
            res = seeTxt(nowBlock, name)
            if res == '没找到该文件':
                print(res)
                continue
            print(name + '的信息为:', end='')
            print(res)
        # 删除文件
        elif command.startswith('delete '):
            name = command.split(' ')[1]
            res = deleteFile(nowBlock, name)
            print(res)
        else:
            print('输入错误，请输入command help查看指令')


if __name__ == "__main__":
    iniFile()
    fileController()
