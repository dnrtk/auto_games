#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
import time
import datetime
import threading
import subprocess
from pathlib import Path

from adb_utils import AdbUtils

IMG_SCALE = 0.25

class ScreenProcClass():
    def __init__(self, templatePath='./template'):
        path = Path(templatePath)
        templateFileList = list(path.glob('**/*.png'))
        self.templateImgList = {}
        for templateFile in templateFileList:
            baseName = templateFile.stem
            tempImg = cv2.imread(os.path.abspath(templateFile))

            self.templateImgList[baseName] = self.resizeImage(tempImg, IMG_SCALE)

    def checkTemplate(self, srcImg, templateName):
        matchRes = False
        matchPos2 = (0, 0)
        outImg = srcImg.copy()

        if templateName in self.templateImgList:
            tempImg = self.templateImgList[templateName]
            tempWidth = tempImg.shape[1]
            tempHeight = tempImg.shape[0]

            res = cv2.matchTemplate(outImg, tempImg, cv2.TM_CCOEFF_NORMED)
            threshold = 0.70    #類似度の閾値
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):
                matchRes = True
                cv2.rectangle(outImg, pt, (pt[0] + tempWidth, pt[1] + tempHeight), (0,0,255), 2)
                matchPos = (int(pt[0]+(tempWidth/2)), int(pt[1]+(tempHeight/2)))
                matchPos2 = (int(matchPos[0]/IMG_SCALE), int(matchPos[1]/IMG_SCALE))
                break
        
        return matchRes, matchPos2, outImg

    def checkTemplateAll(self, srcImg):
        posDict = {}
        outImg = self.resizeImage(srcImg.copy(), IMG_SCALE)
        for templateName in self.templateImgList.keys():
            matchRes, matchPos, outImg = self.checkTemplate(outImg, templateName)
            if(matchRes):
                posDict[templateName] = matchPos
        return posDict, outImg

    def resizeImage(self, inImg, scale=1.0):
        width = int(inImg.shape[1] * scale)
        height = int(inImg.shape[0] * scale)
        outImg = cv2.resize(inImg, (width, height))
        return outImg


class OperationClass():
    def __init__(self):
        self.adbInstance = AdbUtils.getInstance()

    def tap(self, pos, loopCount=1):
        self.adbInstance.tap(pos, loopCount)

    def swipe(self, startPos, endPos, loopCount=1):
        self.adbInstance.swipe(startPos, endPos, loopCount=1)

def main():
    # マッチング用初期化
    sp = ScreenProcClass('./smp_template')

    # 操作用初期化
    adbInstance = AdbUtils.getInstance()
    opeInstance = OperationClass()

    count = 0
    while(True):
        count += 1
        print('start {}'.format(count))

        print('Enemy Name and Detail')
        opeInstance.tap((720, 1780))
        time.sleep(1)

        print('Boss Battle')
        for attackLoopCount in range(100):
            print('attack {}'.format(attackLoopCount))
            # opeInstance.tap((340, 2100))    # skill 2
            # opeInstance.tap((340, 2250))    # skill 2 & 3
            opeInstance.tap((340, 2350))    # skill 3
            time.sleep(0.5)

            if attackLoopCount % 10 == 0:
                img = adbInstance.screenCapCv2()
                matchRes, matchPos, outImg = sp.checkTemplate(img, 'ok')
                if matchRes:
                    break
        # time.sleep(15)

        print('Result')
        opeInstance.tap((710, 2540))
        time.sleep(1)

        print('Event Point')
        opeInstance.tap((710, 2260))
        time.sleep(1)

        print('Receive')
        img = adbInstance.screenCapCv2()
        matchRes, matchPos, outImg = sp.checkTemplate(img, 'ng')
        if matchRes:
            # この画面がある場合のみ
            print('Receive ON {}'.format(matchPos))
            opeInstance.tap(matchPos)
        time.sleep(5)

        print('Exp')
        opeInstance.tap((710, 2570))
        time.sleep(3)

        print('Quest Bonus')
        opeInstance.tap((710, 1800))
        time.sleep(3)

        print('Get item')
        opeInstance.tap((710, 1910))
        time.sleep(1)

        print('Next of Retry')
        opeInstance.tap((1190, 2600))
        time.sleep(1)

        print('Confirm')
        opeInstance.tap((1020, 1990))

        time.sleep(15)

if __name__ == '__main__':
    main()
