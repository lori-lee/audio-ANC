#!/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as GUI
import tkMessageBox as MB
import ctypes as CT
import os as OS
import thread as TH
import serial as SL
import menu as MN
import devicelist as DL
import startstop as SS
import recplay as RP
import plotter as PL
import status as ST
import time as TM
import player as PY
import targets as TG
import widget as WG
import menu as MU
import observers as OBS

class ApplicationStates:
    ST_APP_CREATED = 'app_created'
    ST_APP_TEST_MENU_CLICKED    = 'app_test_menu_clicked'
    ST_APP_DEVICE_MENU_CLICKED  = 'app_device_menu_clicked'
    ST_APP_CONFIG_MENU_CLICKED  = 'app_config_menu_clicked'
    ST_APP_CLOSE_BTN_CLICKED    = 'app_close_btn_clicked'
#
class Application(WG.Widget):

    ST_INIT     = 0x0
    ST_ON_GOING = 0x01
    ST_DONE     = 0x02
    ST_STOPPED  = 0x03
    #
    def __init__(self, **kwargsv):
        WG.Widget.__init__(self, None)
        self.initWindow(**kwargsv)
        self.logPageSize = kwargsv.get('logsize') if kwargsv.has_key('logsize') else 45
        #
        self.logMutex = TH.allocate_lock()
        self.logList  = []
        #
        # 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
        # (11-10: LinkIn_R), (9-8: LinkIn_L), (7-6: FB_R), (5-4: FB_L), (3-2: FF_R), (1-0: FF_L)
        self.devices = ({'name': 'FF'}, {'name': 'FB'}, {'name': 'LINKIN'})
        self.setState(ApplicationStates.ST_APP_CREATED)
    #
    def initWindow(self, **kwargsv):
        self.widget = GUI.Tk()
        winUser32   = CT.windll.user32
        self.width  = self.getParamValue('width', winUser32.GetSystemMetrics(0), **kwargsv)
        self.height = self.getParamValue('height', winUser32.GetSystemMetrics(1), **kwargsv)
        self.widget.geometry('%dx%d' % (self.width, self.height));
        #
        self.widget['bg'] = kwargsv.get('bg') if kwargsv.has_key('bg') else '#FFF'
        self.threads = []
        logoFile = OS.path.dirname(__file__) + '/logo.ico'
        if OS.path.isfile(logoFile):
            self.widget.iconbitmap(logoFile)
        self.title = kwargsv.get('title') if kwargsv.has_key('title') else u'音频自动测试机'
        self.widget.title(self.title)
        self.menu  = MU.ApplicationMenu(self)
        OBS.MenuClickObserver(self.menu)
        return self
    #
    def initAll(self):
        self.deviceList     = DL.DeviceList(self)
        self.menuBar        = MN.Menu(self)
        self.btnGroup       = SS.ButtonGroup(self)
        self.audioRecPlayer = RP.RecPlayer(self)
        self.plotter        = PL.Plotter(self)
        XY = self.deviceList.XY
        self.labelFrame = GUI.LabelFrame(self.widget, text = u'【进度详情】')
        self.labelFrame.config(width = 580, height = 860)
        self.labelFrame.place(x = 10, y = XY[1])
        self.progressTxt = GUI.Message(self.labelFrame, width = 580)
        self.progressTxt.place(x = 0, y = 0)
        #
    #
    def run(self):
        self.widget.mainloop()
    #
    def startTest(self, *argvs, **kwargvs):
        if 0 == self.deviceList.targetsChecked:
            self.appendLog(u'请先选择需要测试的设备')
            # MB.showwarning(u'错误', u'请先选择需要测试的设备', command = None)
            return self
        self.appendLog(u'开始测试，当前模式为: [%s]' % (u'标准模式' if self.isStandardMode() else u'测试模式'))
        self.progress = self.ST_ON_GOING
        self.setVolume(0.5, 0.5)
        fSecStart = TM.time()
        for id in self.deviceList.targets:
            if False == self.deviceList.targets[id]['checked']:
                continue
            self.appendLog(u'%s当前设备【%s】%s' % ('-'*30, TG.Targets.list[id]['name'], '-' * 30))
            for channel in (0, 1):
                self.appendLog(u'开始测试: [%s]声道' % ((u'左', u'右')[channel]))
                if self.switchOn(id, channel):
                    self.appendLog(u'开关打开成功')
                    self.audioRecPlayer.playrec(id, channel)
                else:
                    self.appendLog(u'开关打开【失败】，略过')
        self.appendLog(u'%s测试结束,耗时:%f秒' % (u'标准模式' if self.isStandardMode() else u'测试模式', TM.time() - fSecStart))
        return self
    #
    def listen(self, event):
        if SS.ButtonGroup.BTN_START == event.data['value']:
            TH.start_new_thread(self.startTest, (0,1))
        else:
            self.appendLog(u'已停止测试')
            self.progress = self.ST_STOPPED
            return self
            TH.start_new_thread(
                self.audioRecPlayer.record,
                (event.type,)
        )
        return self
    #
    def switchOn(self, device, channel):
        return self.onoffSwitch(device, channel, 1)
    #
    def switchOff(self, device, channel):
        return self.onoffSwitch(device, channel, 0)
    #
    def onoffSwitch(self, device, channel, onoff):
        return True
        try:
            serialCOM = None
            serialCOM = SL.Serial('COM5', baudrate = 115200, timeout = 1)
            if not serialCOM.isOpen():
                serialCOM.open()
            device = min(2, max(device, 0))
            command = (0xF << device) if onoff else 0
            serialCOM.write('sw' + chr(command & 0xFF) + chr((command >> 8) & 0xFF) + '\r')
            response = serialCOM.readline()
            self.appendLog(u'端口OK')
        except Exception, e:
            response = False
            self.appendLog(u'打开失败' + e.message)
        finally:
            if serialCOM:
                serialCOM.close()
        self.appendLog(u'端口返回:' + response)
        return response.upper().find('OK') >= 0
    #
    def setVolume(self, leftVol, rightVol):
        winmm = CT.windll.winmm
        def normVol(vol):
            if vol <= 0: vol = 0
            elif vol < 1 or not cmp(type(vol), type(0.0)):
                vol = int(vol * 0xFFFF)
            vol = min(0xFFFF, vol)
            return vol
        #
        leftVol = normVol(leftVol)
        rightVol= normVol(rightVol)
        winmm.waveOutSetVolume(None, leftVol + (rightVol << 16))
        return self
    #
    def getWaveSource(self):
        return r'D:\LineIn.wav'
        #return r'D:\WS_1.wav'
        #return r'D:\Projects\1KHZ.wav'
        return OS.path.dirname(__file__) + '/bibi.wav'
    #
    def appendLog(self, message, prefixTime = True):
        self.logMutex.acquire()
        if prefixTime:
            message = '[%.3f]%s' % (TM.time(), message)
        self.logList.append(message)
        self.logDirty = True
        self.logMutex.release_lock()
        self.updateLog()
        return self
    #
    def isStopped(self):
        return self.ST_STOPPED == self.progress
    #
    def updateLog(self):
        if self.logDirty and (not self.isStopped()):
            startIndex = max(0, len(self.logList) - self.logPageSize)
            message = '\n'.join(self.logList[startIndex:])
            self.progressTxt.config(text = message)
        return self
    #
    def isStandardMode(self):
        return self.getCurrentMode() == DL.DeviceList.MODE_STD
    #
    def isTestMode(self):
        return self.getCurrentMode() == DL.DeviceList.MODE_TEST
    #
    def getCurrentMode(self):
        return self.deviceList.mode
    #
def logTest(*argvs, **kw):
    import random as RD
    while True:
        app.appendLog(u'测试日志行测试日志行测试日志行测试日志测试日志行' + str(RD.randint(1, 65536)))
        TM.sleep(0.01 * RD.randint(1, 10))
    TH.exit()

if __name__ == '__main__':
    app = Application()
    app.run()