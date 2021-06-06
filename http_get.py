#!/usr/bin/env python3
import re
import socket
import sys
import ssl


def typeOfProtocal(link):
    pars = re.findall('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', link)
    return pars[0][1], pars[0][3], pars[0][4]


def splitResponse(response):
    splitData = response.split(' ')
    return splitData[1], splitData[2]


def parsHeader():
    dictionary = {}
    while True:
        header = f.readline().decode('ASCII')
        print(header)
        if header == '\r\n':
            return dictionary
        dictionary[header.split(': ')[0].lower()] = header.split(': ')[1].lower()


def redirection(loc):
    return re.findall('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', loc.strip())[0][4]


def checkStatusResponse(code, status, dictionary, path):
    if code == '200':
        return True, path
    if code == '301' or code == '302' or code == '303' or code == '307' or code == '308':
        newPath = redirection(dictionary['location'])
        return False, newPath
    sys.stderr.write(code + status)
    f.close()
    sys.exit(1)


def printContent(dictionary):
    if 'transfer-encoding' in dic:
        while True:
            chunkLength = f.readline().decode('ASCII')
            contentLength = int(chunkLength, 16)
            chunk = f.read(contentLength)
            sys.stdout.buffer.write(chunk)
            if not chunk:
                break
            f.readline()
    elif 'content-length' in dic:
        contentLength = int(dic['content-length'])
        contentData = f.read(contentLength)
        sys.stdout.buffer.write(contentData)


urlLink = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dic = {}
protocolType, hostName, pathTail = typeOfProtocal(urlLink)

if protocolType == 'https':
    s.connect((hostName, 443))
    s = ssl.wrap_socket(s)
else:
    s.connect((hostName, 80))

while True:
    f = s.makefile('rwb')
    f.write(f'GET {pathTail} HTTP/1.1\r\n'.encode('ASCII'))
    f.write(f'Host: {hostName}\r\n'.encode('ASCII'))
    f.write(f'Accept-charset: UTF-8\r\n\r\n'.encode('ASCII'))
    f.flush()

    codeResponse, statusResponse = splitResponse(f.readline().decode('ASCII'))
    dic = parsHeader()
    statusCondition, pathTail = checkStatusResponse(codeResponse, statusResponse, dic, pathTail)

    if statusCondition:
        break
    else:
        f.close()


printContent(dic)
f.flush()
f.close()
sys.exit(0)
