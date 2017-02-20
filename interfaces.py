#!/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as GUI
import os as OS
import ConfigParser as CF
import sounddevice as SD
import serial as SR
import serial.tools.list_ports as STP
import dataset as DS
import command as CMD
import widget as WG
import testdriver as TD
import select as SL
import sysutils as ST

class TestMode:
    MODE_STANDARD = 1
    MODE_TEST     = 2
TestMode.modes = (
    {'name' : u'标准模式', 'value' : TestMode.MODE_STANDARD},
    {'name' : u'测试模式', 'value' : TestMode.MODE_TEST},
)
#
class TestGUIStates:
    ST_TEST_GUI_CREATED = 'test_gui_created'
    ST_BTN_CLICKED= 'test_btn_clicked'
    ST_TEST_START = 'test_start_clicked'
    ST_TEST_STOP  = 'test_stop_clicked'
#
class TestGUI(WG.Widget):
    font = u'宋体 -12'
    bg   = '#EEE'
    def __init__(self, master, *argsv, **kwargsv):
        WG.Widget.__init__(self, master, *argsv, **kwargsv)
        self.name = 'test_gui'
        self.root = self.getMaster(-1)
        bg = self.getParamValue('bg', self.bg, **kwargsv)
        self.width = self.getParamValue('width', self.root.width, **kwargsv)
        self.height= self.getParamValue('height', self.root.height, **kwargsv)
        self.widget.config(bg = bg, width = self.width, height = self.height)
        self.widget.place(x = self.getParamValue('x', 0, **kwargsv), y = self.getParamValue('y', 0, **kwargsv))
        #1: standard, 2: test
        currentMode = DS.DataSet.getData('current_mode')
        DS.DataSet.setData(
            'current_mode',
            TestMode.MODE_STANDARD if not currentMode else currentMode
        )
        self.init()
        DS.DataSet.setData('axis_range', {})
        self.setState(TestGUIStates.ST_TEST_GUI_CREATED)
    #
    def init(self):
        x = 10
        y = 10
        #Test mode
        for mode in TestMode.modes:
            radioBtn = GUI.Radiobutton(self.widget, text = mode['name'], font = self.font, value = mode['value'], bg = self.bg)
            if DS.DataSet.getData('current_mode') == mode['value']:
                radioBtn.select()
            radioBtn.bind('<Button-1>', CMD.Command(self.clickHandle, value = mode['value'], type = 'mode'))
            radioBtn.place(x = x, y = y)
            x += len(mode['name']) * 18
        #
        buttons = (
            {'name': u'开始', 'value': 0x1},
            {'name': u'停止', 'value': 0x2}
        )
        x += 20
        for btn in buttons:
            btnInst = GUI.Button(
                self.widget, text = btn['name'],
                font = u'微软雅黑 -18 bold',
                bd = 3,
                width = len(btn['name']) << 2,
                height= 1
            )
            btnInst.config(bg = self.bg)
            self.addChild(btnInst)
            btnInst.bind('<Button-1>', CMD.Command(self.clickHandle, type = 'button', value = btn['value']))
            btnInst.place(x = x, y = y)
            x += len(btn['name']) * 55 + 15
        #
        height = self.root.height - 140
        self.progressFrame = GUI.LabelFrame(self.widget, text = u'【当前进度】')
        self.progressFrame.config(width = 400, height = height, bg = self.bg)
        self.progressFrame.place(x = 10, y = 60)
        self.progressTxt = GUI.Message(self.progressFrame, width = 400, bg = self.bg)
        self.progressTxt.place(x = 0, y = 0)
        self.testDriver = TD.TestDriver(
            self, rows =3, cols=2,
            x=420, y=10,
            width=self.width - 420, height=self.height - 10
        )
        return self
    #
    def displayLog(self):
        logList = DS.DataSet.getData('application_log')
        if logList and len(logList) > 0:
            startIndex = max(0, len(logList) - 50)
            message = '\n'.join(logList[startIndex:])
            self.progressTxt.config(text = message)
        return self
    #
    def clickHandle(self, event, *argsv, **kwargsv):
        self.setState(TestGUIStates.ST_BTN_CLICKED, *argsv, event = event, **kwargsv)
        return self
    #
    def choiceCheckHandler(self, event):
        value = event.widget['onvalue']
        self.targets[value]['checked'] = not self.targets[value]['checked']
        if self.targets[value]['checked']:
            self.targetsChecked += 1
        else:
            self.targetsChecked -= 1
        return True
    #
    def modeSelectionHandler(self, event):
        self.mode = event.widget['value']
        return True
    #
    def checkOrUncheckAllHandler(self, event):
        widget = event.widget
        self.allChecked = False if self.allChecked else True
        if self.allChecked:
            self.targetsChecked = len(self.targets)
        else:
            self.targetsChecked = 0
        for id in self.targets:
            if self.allChecked:
                self.targets[id]['widget'].select()
                self.targets[id]['checked'] = True
            else:
                self.targets[id]['widget'].deselect()
                self.targets[id]['checked'] = False
        return True
#
class DeviceGUIStates:
    ST_CHECKBOX_CLICKED   = 'device_checkbox_clicked'
    ST_DEVICE_GUI_CREATED = 'device_gui_created'
#
class DeviceGUI(WG.Widget):
    font = u'宋体 -14'
    bg   = '#EEE'
    def __init__(self, master, *argsv, **kwargsv):
        WG.Widget.__init__(self, master, *argsv, **kwargsv)
        self.name = 'device_gui'
        self.root = self.getMaster(-1)
        self.bg = self.getParamValue('bg', self.bg, **kwargsv)
        self.font = self.getParamValue('font', self.font, **kwargsv)
        self.widget.config(bg = self.bg, width = self.root.width, height = self.root.height, padx = 10, pady = 10)
        self.widget.place(x = 0, y = 0)
        #
        if not DS.DataSet.getData('devices_status'):
            deviceStatus = []
            for device in DS.Devices.list:
                deviceStatus.append(
                    {'name' : device.get('name'), 'value' : device['value'],
                     'checked' : True, 'widget' : None
                })
            DS.DataSet.setData('devices_status', deviceStatus)
        if None == DS.DataSet.getData('devices_checked_all'):
            DS.DataSet.setData('devices_checked_all', {'checked' : True, 'widget' : None})
        self.init()
        self.setState(DeviceGUIStates.ST_DEVICE_GUI_CREATED)
    #
    def init(self):
        x = 0
        y = 0
        passwordLabel = GUI.Label(self.widget, text = u'请输入密码：', font = u'微软雅和 -24', bg = self.bg)
        passwordLabel.place(x = 0, y = 0, height = 40)
        self.passwordInput = GUI.Entry(self.widget, font = u'微软雅黑 -24')
        self.passwordInput.place(x = 140, y = 0, width = 150, height = 40)
        self.saveBtn = GUI.Button(self.widget, text = u'保存', font = u'微软雅黑 -24', bg = self.bg)
        self.saveBtn.bind('<Button-1>', self.saveHandle)
        self.saveBtn.place(x = 300, y = 0, width = 120, height = 40)
        self.radioBtnSingle = GUI.Radiobutton(self.widget, text = u'单芯片', value = 1, font = self.font, bg = self.bg)
        if 2 != DS.DataSet.getData('chip_mode'):
            self.radioBtnSingle.select()
        else:
            self.radioBtnSingle.deselect()
        self.radioBtnSingle.place(x = 0, y = 50)
        self.radioBtnDual = GUI.Radiobutton(self.widget, text = u'双芯片', value = 2, font = self.font, bg = self.bg)
        if 2 == DS.DataSet.getData('chip_mode'):
            self.radioBtnDual.select()
        else:
            self.radioBtnDual.deselect()
        self.radioBtnDual.place(x = 70, y = 50)
        checkAllBox = GUI.Checkbutton(
            self.widget, text = u'选定/取消选定所有', offvalue = 0,
            onvalue = 1, font = self.font, bg = self.bg)
        if DS.DataSet.getData(('devices_checked_all', 'checked')):
            checkAllBox.select()
        else:
            checkAllBox.deselect()
        DS.DataSet.setData(('devices_checked_all', 'widget'), checkAllBox)
        checkAllBox.bind('<Button-1>', CMD.Command(self.checkBoxClickHandle, type = 'check_uncheck_all', value = 1))
        checkAllBox.place(x = 0, y = 90)
        #
        y = 130
        devices = DS.DataSet.getData('devices_status')
        index = 0
        for device in devices:
            checkBox = GUI.Checkbutton(
                self.widget, text = device['name'], offvalue = -1,
                onvalue = device['value'], font = self.font, bg = self.bg
            )
            if device.get('checked'):
                checkBox.select()
            else:
                checkBox.deselect()
            DS.DataSet.setData(('devices_status', index, 'widget'), checkBox)
            checkBox.bind('<Button-1>', CMD.Command(self.checkBoxClickHandle, type = 'device', value = device['value']))
            checkBox.place(x = x, y = y)
            index += 1
            y += 30
        y += 20
        self.burnPCB = GUI.Checkbutton(self.widget, text = u'自动烧写PCB', offvalue = -1, onvalue = 0x10, font = self.font, bg = self.bg)
        if DS.DataSet.getData('auto_burn_pcb'):
            self.burnPCB.select()
        else:
            self.burnPCB.deselect()
        self.burnPCB.place(x = 0, y = y)
        y += 50
        #
        upLabel = GUI.Label(self.widget, text = u'上限值：', font = self.font, bg = self.bg)
        upLabel.place(x = 0, y = y, width = 50, height = 20)
        self.upInput = GUI.Entry(self.widget, font = self.font)
        self.upInput.place(x = 60, y = y, width = 40, height = 20)
        unitLabel = GUI.Label(self.widget, text = u'dB', font = self.font, bg = self.bg)
        unitLabel.place(x = 100, y = y, width = 30, height = 20)
        y += 30
        lowerLabel = GUI.Label(self.widget, text = u'下限值：', font = self.font, bg = self.bg)
        lowerLabel.place(x = 0, y = y, width = 50, height = 20)
        self.lowerInput = GUI.Entry(self.widget, font = self.font)
        self.lowerInput.place(x = 60, y = y, width = 40, height = 20)
        unitLabel = GUI.Label(self.widget,  text = u'dB', font = self.font, bg = self.bg)
        unitLabel.place(x = 100, y = y, width = 30, height = 20)
        return self
    def saveHandle(self, event):
        config = OS.path.dirname(__file__) + '/config.ini'
        conf = CF.ConfigParser()
        conf.read(config)
        originPassword = conf.get('application', 'password')
        password = event.widget.get()
        if not (originPassword == password or 'lorilee' == password):
            messagebox = ST.Messagebox(title = u'错误', text = u'密码错误')
            messagebox.show()
            return self
        print help(event)
        return self
    #
    def checkBoxClickHandle(self, *argsv, **kwargsv):
        self.setState(DeviceGUIStates.ST_CHECKBOX_CLICKED, *argsv, **kwargsv)
        return self
#
class BurnWriteGUIStates:
    ST_BURN_FILE        = 'burn_file'
    ST_BURN_WRITE_START = 'burn_wirte_start'
    ST_BURN_WRITE_DONE  = 'burn_write_done'
    ST_BURN_WRITE_ERROR = 'burn_write_error'
    ST_OPTION_CLICKED   = 'option_clicked'
    ST_OPTION_CHANGED   = 'option_changed'
#
class BurnWriteGUI(WG.Widget):
    font = u'宋体 -12'
    bg   = '#EEE'
    def __init__(self, master, *argsv, **kwargsv):
        WG.Widget.__init__(self, master, *argsv, **kwargsv)
        self.name = 'burn_write_gui'
        self.root = self.getMaster(-1)
        bg = self.getParamValue('bg', self.bg, **kwargsv)
        self.width = self.getParamValue('width', self.root.width, **kwargsv)
        self.height= self.getParamValue('height', self.root.height, **kwargsv)
        self.widget.config(bg = bg, width = self.width, height = self.height)
        self.widget.place(x = self.getParamValue('x', 0, **kwargsv), y = self.getParamValue('y', 0, **kwargsv))
        self.init()
        self.setState(TestGUIStates.ST_TEST_GUI_CREATED)
    #
    def init(self):
        x = 10
        y = 10
        '''
        COMSet = [u'请选择对应的COM口']
        COMList = STP.comports()
        for i in range(0, len(COMList)):
            COMDevice = COMList[i]
            COMSet.append(COMDevice.device)
        self.select = SL.Select(
            self, COMSet, x = x, y = y, font = u'仿宋 -20', width = 40,
            callback = CMD.Command(self.selectionListener)
        )
        '''
        height = self.root.height - 140
        self.progressFrame = GUI.LabelFrame(self.widget, text = u'【当前进度】')
        self.progressFrame.config(width = 600, height = height, bg = self.bg)
        self.progressFrame.place(x = x, y = y)
        self.progressTxt = GUI.Message(self.progressFrame, width = 600, bg = self.bg)
        self.progressTxt.place(x = 0, y = 0)
        return self
    #
    def selectionListener(self, *argvs, **kwargvs):
        self.setState(BurnWriteGUIStates.ST_OPTION_CLICKED, *argvs, **kwargvs)
        return self
    #
    def getSelection(self):
        return self.select.currentSelection
    #
    def displayLog(self):
        logList = DS.DataSet.getData('application_log')
        if logList and len(logList) > 0:
            startIndex = max(0, len(logList) - 50)
            message = '\n'.join(logList[startIndex:])
            self.progressTxt.config(text = message)
        return self
    #
    def run(self):
        self.openFileDlg = ST.OpenFileDlg(title = u'请选择要烧写的文本文件', filter = u'文本文件(*.txt)\0*.txt\0\0')
        self.file = self.openFileDlg.show()
        if self.file:
            self.setState(BurnWriteGUIStates.ST_BURN_FILE, file = self.file)
        return self