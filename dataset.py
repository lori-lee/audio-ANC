#!/bin/env python
#-*- coding: utf-8 -*-
import copy as CP
import thread as TH

#
class Devices:
    list = (
        #{'name' : u'烧写芯片', 'value' : 0x10,},
        {'name' : 'MIC FF', 'value' : 0x1,},
        {'name' : 'MIC FB', 'value' : 0x2,},
        {'name' : 'LineIn', 'value' : 0x3,}
    )
    @staticmethod
    def anyChecked():
        for device in DataSet.getData('devices_status'):
            if device.get('checked'):
                return True
        return False
#
class DataSet:
    #
    _currentData_ = {
        'config_com' : {'name' : 'COM6', 'rate' : 38400, 'timeout' : 0.1, 'tries' : 1,},
        'switch_com' : {'name' : 'COM5', 'rate' : 115200, 'timeout' : 0.5,},
        'help_usage' : u'1.[配置]->[烧写PCB]选择要烧写的数据文件\n2.[配置]->[导入音频文件]选择输入的音频\n3.[界面]->[设备]确认要测试的设备\n4.[界面]->[测试]开始测试',
        'help_about_me' : u'作者：Lori Lee\n版权所有@紫连草科技',
        'switch_mask' : {
            'MIC_FF' : (0xA088, 0x5044),
            'MIC_FB' : (0xA022, 0x5011),
            'LineIn' : (0xAA00, 0x5500),
        }
    }
    dataMutex     = TH.allocate_lock()
    #
    @staticmethod
    def setData(key, value):
        DataSet.dataMutex.acquire()
        target = DataSet._currentData_
        if type(key) in (type(()), type([])):
            key = list(tuple(key))
            lastKey = key.pop()
            for k in key:
                if (type({}) == type(target) and not target.has_key(k)) or\
                    (type(target) in (type([]), type(())) and len(target) <= k):
                    target[k] = {}
                target = target[k]
            target[lastKey] = value
        else:
            DataSet._currentData_[key] = value
        DataSet.dataMutex.release()
        return DataSet
    #
    @staticmethod
    def getData(key, copy = False):
        target = DataSet._currentData_
        if type(key) in (type(()), type([])):
            for k in key:
                if (type({}) == type(target) and not target.has_key(k))\
                        or (type(target) in (type(()), type([])) and len(target) <= k):
                    target = None
                    break
                target = target[k]
        else:
            target = None if not DataSet._currentData_.has_key(key) else DataSet._currentData_[key]
        return CP.deepcopy(target) if copy else target
#
if __name__ == '__main__':
    DataSet.setData('first', 'value-first')
    print DataSet.getData('first')
    DataSet.setData(('second', 'second-1'), '3-level key nested')
    print DataSet.getData(['second', 'second-1'])