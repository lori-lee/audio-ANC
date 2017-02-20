#!/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as GUI
import sounddevice as SD
import targets as TG

class DeviceList:
    MODE_STD = 0x10
    MODE_TEST= 0x20
    font = u'宋体 -12'
    def __init__(self, master):
        self.parent = master
        self.widget = GUI.Frame(master.getWidget())
        self.widget.config(bg = '#FFF', width = 500, height = 500)
        self.devices  = {}
        self.targets  = {}
        self.allChecked = True
        self.mode = DeviceList.MODE_STD
        self.XY   = [0, 0]
        self.targetsChecked = len(TG.Targets.list)
        self.initDeviceList()
    #
    def initDeviceList(self):
        allDevices = SD.query_devices()
        for i in range(len(allDevices)):
            device = allDevices[i]
            name = device.get('name').upper()
            if True or name.find('STEINBERG') >= 0:
            #if name.find('STEINBERG') >= 0:
                self.devices[i] = {
                    'id': i, 'name': name, 'device': device, 'checked': True
                }
        if not len(self.devices):
            return self
        candidateModes = [
            {'text': u'标准模式', 'value': DeviceList.MODE_STD},
            {'text': u'测试模式', 'value': DeviceList.MODE_TEST}
        ]
        x = 10
        y = 10
        for i in range(len(candidateModes)):
            mode = candidateModes[i]
            radioBtn = GUI.Radiobutton(self.widget, text = mode['text'], font = DeviceList.font, value = mode['value'])
            if DeviceList.MODE_STD == mode['value']:
                radioBtn.select()
            radioBtn.bind('<Button-1>', self.modeSelectionHandler)
            radioBtn.place(x = x, y = y)
            x += len(mode['text']) * 18
        #
        checkAllBox = GUI.Checkbutton(
            self.widget, text = u'选定/取消选定所有', offvalue = 0,
            onvalue = 1, font = DeviceList.font)#state = GUI.DISABLED)
        checkAllBox.bind('<Button-1>', self.checkOrUncheckAllHandler)
        checkAllBox.select()
        checkAllBox.place(x = x + 50, y = y)
        y += 40
        '''
        for i in self.devices:
            device   = self.devices[i]['device']
            deviceID = self.devices[i]['id']
            labelTxt = ' - '.join([
                        u'设备号:' + str(deviceID),
                        device.get('name'),
                        SD.query_hostapis(device.get('hostapi')).get('name'),
                        str(device.get('max_input_channels')) + ' IN / ' + str(device.get('max_output_channels')) + ' OUT'
            ])
            self.devices[i]['label'] = labelTxt
            checkBox = GUI.Checkbutton(
                self.widget, text = labelTxt, offvalue = 0,
                onvalue = deviceID, font = DeviceList.font
            )
            checkBox.select()
            checkBox.bind('<Button-1>', self.choiceCheckHandler)
            self.devices[i]['widget'] = checkBox
            checkBox.place(x = 10, y = y)
            y += 20
        '''
        index = 0
        for target in TG.Targets.list:
            checkBox = GUI.Checkbutton(
                self.widget, text = target['name'], offvalue = -1,
                onvalue = index, font = DeviceList.font
            )
            checkBox.select()
            checkBox.bind('<Button-1>', self.choiceCheckHandler)
            self.targets[index] = {'widget' : checkBox, 'checked' : True}
            checkBox.place(x = 10, y = y)
            y += 20
            index += 1
        self.XY = [x, y]
        self.widget.place(x = 0, y = 0)
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