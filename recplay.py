#!/bin/env python
# -*- coding: utf-8 -*-
import sounddevice as SD
import soundfile
import wave
import numpy as NP
import ctypes
import struct
import thread as TH
import pylab as PL
import player as PY
import recorder as RC

class RecPlayer:
    def __init__(self, master):
        self.parent = master
        self.waveDir= None
        #
        self.windll = ctypes.windll
        self.kernel32 = self.windll.kernel32
    #
    def asycPlay(self, outDeviceId, ndata):

        return self
    def playrec(self, target, channel):
        fp = self.parent.getWaveSource()
        file = wave.open(fp, 'rb')
        if file: self.parent.appendLog(u'打开文件:[' + fp + ']OK')
        else: self.parent.appendLog(u'打开文件:[' + fp + u']失败')
        frames = file.readframes(file.getnframes())
        self.parent.appendLog(u'音频文件参数:' + str(file.getparams()))
        origin = NP.fromstring(frames, dtype = (NP.int8, NP.int16)[file.getsampwidth() - 1])
        ndata = NP.fromstring(frames, dtype = (NP.int8, NP.int16)[file.getsampwidth() - 1])
        ndata.shape = [-1, file.getnchannels()]
        #
        self.parent.appendLog(u'开始播放测试')
        self.player = PY.Player(2, ndata, file.getframerate())
        self.player.play()
        #return self
        self.parent.appendLog(u'开始录音测试')
        self.recorder = RC.Recorder(1, len(ndata))
        self.recorder.rec()
        self.parent.appendLog(u'获取录音数据')
        recData = self.recorder.getData()
        self.parent.appendLog(u'录音数据获取完成')
        #
        self.parent.appendLog(u'开始对输入绘图')
        leftData = NP.array(tuple(e[0] for e in ndata))
        if 1 == ndata.shape[1]:
            rightData = leftData[:]
        else:
            rightData= NP.array(tuple(e[1] for e in ndata))
        self.parent.plotter.framerate = file.getframerate()
        self.parent.plotter.draw(leftData, rightData)
        self.parent.appendLog(u'输入绘图结束')
        #
        self.parent.appendLog(u'开始对输出绘图')
        leftData = NP.array(tuple(e[0] for e in recData))
        rightData= NP.array(tuple(e[1] for e in recData))
        self.parent.plotter.draw(leftData, rightData, (target << 1) + channel + 1)
        self.parent.appendLog(u'输出绘图结束')
        #
        self.parent.appendLog(u'录音数据参数:声道数[%d],帧数:[%d], 数据宽度:[%s]' % (recData.shape[1], recData.shape[0], recData.dtype.name))
        #self.parent.appendLog(u'回放录音')
        #self.player2 = PY.Player(2, recData, 44100)
        #self.player2.play()
        #self.player2.wait()
        #self.parent.appendLog(u'回放结束')
        return self
        #
        SD.play(NP.array(()))
        self.parent.appendLog(u'开始测试')
        nRecData = SD.playrec(ndata, channels = 2, dtype = NP.int16, input_mapping = [1, 2])
        #nRecData = ndata
        SD.wait()
        self.parent.appendLog(u'测试结束，开始绘图')
        leftData = NP.array(tuple(e[0] for e in nRecData))
        rightData= NP.array(tuple(e[1] for e in nRecData))
        self.parent.plotter.draw(leftData, rightData, (target << 1) + channel + 1)
        self.parent.appendLog(u'绘图完成')
        TH.exit()
        #
        origin.dtype = NP.uint16
        leftData.dtype= NP.uint16
        inputFFT = NP.fft.fft(origin)
        outLeftFFT = NP.fft.fft(leftData)
        outLeftFreq= NP.fft.fftfreq(len(leftData), 1.0 / file.getframerate())
        inputA = inputFFT.real ** 2 + inputFFT.imag ** 2
        outLeftA = outLeftFFT.real ** 2 + outLeftFFT.imag ** 2
        dBList = 10 * NP.log10((outLeftA + 1) / (inputA + 1))
        PL.plot(outLeftFreq, dBList)
        PL.show()
        return self
    #
    def record(self, deviceID):
        SD.play(NP.array(()))
        npRecData = SD.rec(device = 1,
            samplerate = 44100, frames = 10 * 44100,
            channels = 2, blocking = False
        )
        SD.wait()
        print npRecData.shape
        print 'Rec end'
        leftChannel = (frame[0] for frame in npRecData)
        rightChannel= (frame[1] for frame in npRecData)
        print 'sleep begin'
        SD.sleep(2000)
        print 'sleep end'
        SD.play(npRecData, samplerate = 44100, device = 3)
        print 'Play end'
        zipData = npRecData
        #zipData.shape = [1,-1]
        #packData  = struct.pack()
        TH.exit()
        return self
    #
    def play(self, deviceID):
        sourceWav = self.parent.getWaveSource()
        #data, frameRate = soundfile.read(sourceWav, dtype = 'int16')
        file = wave.open(sourceWav, 'rb')
        allFrames = file.readframes(file.getnframes())
        decodeType= (NP.int8, NP.int16, NP.int32)[(file.getsampwidth() >> 1)]
        data = NP.fromstring(allFrames, dtype = decodeType)
        data.shape = (-1, 2)
        frameRate  = file.getframerate()
        SD.default.channels = [2, 1]
        SD.play(data, samplerate = frameRate, device = 3)
        '''
        for i in range(1, 4):
            print('Device ID: %d, channel ID: %d, %d: sleep: %d' % (deviceID, channelID, i, i))
            self.kernel32.Sleep(i * 1000)
        '''

        TH.exit()
        return self