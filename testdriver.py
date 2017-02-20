#!/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as GUI
import matplotlib as MPL
import numpy as NP
import matplotlib.backends.backend_tkagg as MBTK
import matplotlib.figure as FG
import random as RD
import thread as TH
import sounddevice as SD
import wave as WV
import copy as CP
import serial as SL
import widget as WG
import dataset as DS
import sysutils as ST

class Player:
    def __init__(self, deviceID):
        self.deviceID  = deviceID
        self.playMutex = TH.allocate_lock()
    #
    def play(self, ndata, samplerate):
        self.wait()
        self.ndata = ndata
        self.currentFrame = 0
        self.outputStream = SD.OutputStream(
            device     = self.deviceID,
            samplerate = samplerate,
            channels   = ndata.shape[1],
            dtype      = ndata.dtype.name,
            callback   = self.streamFeeder
        )
        self.playMutex.acquire()
        self.frames = ndata.shape[0]
        self.outputStream.start()
        return self
    #
    def streamFeeder(self, outdata, frames, time, status):
        if self.currentFrame >= self.frames:
            self.outputStream.close()
            if self.playMutex.locked():
                self.playMutex.release()
        blocksize = min(self.frames - self.currentFrame, len(outdata))
        outdata[:blocksize] = self.ndata[self.currentFrame : self.currentFrame + blocksize]
        outdata[blocksize:] = 0
        self.currentFrame += blocksize
    #
    def isDone(self):
        return not self.playMutex.locked()
    #
    def wait(self):
        self.playMutex.acquire()
        self.playMutex.release()
        return self
#
class Recorder:
    def __init__(self, device, frames, samplerate):
        self.device = device
        deviceInfo  = SD.query_devices(device)
        self.samplerate = min(samplerate, deviceInfo.get('default_samplerate'))
        self.channels   = deviceInfo.get('max_input_channels')
        self.ndata  = NP.empty((frames, self.channels), dtype = NP.int16)
        self.frames = frames
        self.currentFrame = 0
        self.recMutex = TH.allocate_lock()
    #
    def rec(self):
        self.inputStream = SD.InputStream(
            device     = self.device,
            samplerate = self.samplerate,
            channels   = self.channels,
            dtype      = NP.dtype(NP.int16).name,
            callback   = self.recFeeder,
            latency    = 'low'
            #prime_output_buffers_using_stream_callback = True
        )
        self.recMutex.acquire()
        self.inputStream.start()
        return self
    #
    def recFeeder(self, indata, frames, time, status):
        self.blocksize = min(self.frames - self.currentFrame, len(indata))
        self.ndata[self.currentFrame : self.currentFrame + self.blocksize] = indata[:self.blocksize]
        self.currentFrame += self.blocksize
        if self.currentFrame >= self.frames:
            self.inputStream.close()
            if self.recMutex.locked():
                self.recMutex.release()
    #
    def wait(self):
        self.recMutex.acquire()
        self.recMutex.release()
        return self
    #
    def getData(self, block = True):
        if block:
            self.wait()
        return self.ndata
#
class SwitcherStates:
    ST_SWITCH_ON = 'switch_on'
    ST_SWITCH_ERR= 'switch_error'
    ST_COM_ERR   = 'switch_com_error'
#
class Switcher(WG.Widget):

    def __init__(self, master, *argvs, **kwargvs):
        WG.Widget.__init__(self, master, *argvs, **kwargvs)
        config = DS.DataSet.getData('switch_com')
        try:
            self.serialCOM = SL.Serial(
                config['name'],
                baudrate = config['rate'],
                timeout = config['timeout']
            )
        except Exception, e:
            self.master.doLog(e.message)
            self.setState(SwitcherStates.ST_COM_ERR)
    #
    def open(self, mask):
        if not hasattr(self, 'serialCOM'):
            return self
        if not self.serialCOM.isOpen():
            self.serialCOM.open()
        self.serialCOM.write('sw' + chr((mask >> 8) & 0xFF) + chr(mask & 0xFF) + '\r')
        response = self.serialCOM.readline()
        if -1 == response.upper().find('OK'):
            self.setState(SwitcherStates.ST_SWITCH_ERR)
            return False
        else:
            self.setState(SwitcherStates.ST_SWITCH_ON)
            return True
#
class Plotter(WG.Widget):
    def __init__(self, master, *argvs, **kwargvs):
        WG.Widget.__init__(self, master, *argvs, **kwargvs)
        self.rows = self.getParamValue('rows', 3, **kwargvs)
        self.cols = self.getParamValue('cols', 2, **kwargvs)
        self.framerate = self.getParamValue('framerate', 44100, **kwargvs)
        #
        self.width = self.getParamValue('width', self.master.getWidget()['width'], **kwargvs)
        self.height= self.getParamValue('height', self.master.getWidget()['height'], **kwargvs)
        self.dpi   = 99
        self.figure= FG.Figure(
            figsize = (self.width / self.dpi, self.height / self.dpi), dpi = self.dpi,
            facecolor = '#EEEEEE'
        )
        self.canvas= MBTK.FigureCanvasTkAgg(self.figure, master = self.master.getWidget())
        self.canvas.show()
        self.canvas.get_tk_widget().place(x = 0, y = 0)
    #
    def markStatus(self, grid = 1, text = u'OK', color = 'green'):
        gridRect = self.figure.add_subplot(self.rows, self.cols, grid)
        gridRect.set_xlabel(text, labelpad = -8, fontsize = 6, fontdict = {'color': color})
        return self
    #
    def draw(self, input, output, device, grid = 1, color = 'b'):
        #try:
        gridRect = self.figure.add_subplot(self.rows, self.cols, grid)
        Pyx, freqYX = gridRect.csd(input, output, NFFT = self.framerate / 4, Fs = self.framerate, visible = False)
        Pxx, freqXX = gridRect.csd(output, output, NFFT = self.framerate / 4, Fs = self.framerate, visible = False)
        gridRect.semilogx()
        dB = Pyx * 1.0 / Pxx
        Y  = 20 * NP.log10(abs(dB))
        winSize = 0.1
        coeff = 10 ** (0.5 * winSize)
        index = int(coeff) + 1
        end   = int(len(freqXX) / (coeff))
        fitY  = Y[:index]
        while index <= end:
            _start = int(index / coeff) + 1
            _end   = int(index * coeff) + 1
            fitY = NP.append(fitY, NP.array(sum(Y[_start:_end + 1]) / (_end - _start + 1), dtype = Y.dtype))
            index += 1
        fitY = NP.append(fitY, Y[end + 1:])
        gridRect.plot(freqXX, fitY, color + '-', linewidth = 0.1, label = device)
        gridRect.legend(fancybox = False, edgecolor = 'black', loc = 0, fontsize = 8, framealpha = 0.4)
        gridRect.set_xlabel('Frequency', labelpad = -8, fontsize = 6, fontdict = {'color' : 'red'})
        gridRect.set_xlabel('\nOK', labelpad = -8, fontsize = 6, fontdict = {'color': 'red'})
        gridRect.set_ylabel('Amplitude', labelpad = -4, fontsize = 6)
        for side in ('top', 'right', 'bottom', 'left'):
            gridRect.spines[side].set_linewidth(0.5)
        xmin = 10
        xmax = min(20000, max(freqXX))
        xrange = DS.DataSet.getData(('axis_range', grid, 'x'))
        if xrange:
            xrange = (min(xrange[0], xmin), max(xrange[1], xmax))
        else:
            xrange = (xmin, xmax)
        gridRect.set_xlim(xmin = xrange[0], xmax = xrange[1])
        DS.DataSet.setData(('axis_range', grid, 'x'), xrange)
        ymin = min(Y)
        ymax = max(Y)
        yrange = DS.DataSet.getData(('axis_range', grid, 'y'))
        if yrange:
            yrange = (min(yrange[0], ymin), max(yrange[1], ymax))
        else:
            yrange = (ymin, ymax)
        gridRect.set_ylim(ymin = yrange[0] - 0.5, ymax = yrange[1] + 0.5)
        DS.DataSet.setData(('axis_range', grid, 'y'), yrange)
        if yrange[0] != yrange[1]:
            gridRect.set_yticks(NP.linspace(yrange[0], yrange[1], 10))
        for tick in gridRect.yaxis.get_major_ticks():
            tick.label1.set_fontsize(6)
        for tick in gridRect.xaxis.get_major_ticks():
            tick.label1.set_fontsize(6)
        gridRect.grid(color = 'g', linestyle = '-', linewidth = 0.1)
        self.canvas.show()
        #except Exception, e:
            #self.parent.appendLog(u'绘图发生异常:%s' % e.message)
        return self
    #
    def clearGrid(self, grid = None):
        if None != grid:
            gridRect = self.figure.add_subplot(self.rows, self.cols, grid)
            gridRect.clear()
        else:
            totalGridNum = self.rows * self.cols
            index = 0
            while index < totalGridNum:
                self.clearGrid(index)
                index += 1
        return self
    #
    def saveFigure(self, path):
        if self.figure:
            self.figure.savefig(path)
        return self
#
class TestDriver(WG.Widget):
    def __init__(self, master, *argvs, **kwargvs):
        WG.Widget.__init__(self, master, *argvs, **kwargvs)
        #
        self.inputDevice = SD.default.device[0]
        self.outputDevice= SD.default.device[1]
        self.initAudioInput()
        x = self.getParamValue('x', 0, **kwargvs)
        y = self.getParamValue('y', 0, **kwargvs)
        self.width = self.getParamValue('width', 300, **kwargvs)
        self.height= self.getParamValue('height', 400, **kwargvs)
        self.widget.config(width = self.width, height = self.height, bg = '#EEE')
        self.widget.place(x = x, y = y)
        self.rows = self.getParamValue('rows', 3, **kwargvs)
        self.cols = self.getParamValue('cols', 2, **kwargvs)
        self.currentDeviceIndex = 1
        #
        self.plotter = Plotter(self, width = self.width, height = self.height, rows = self.rows, cols = self.cols)
        self.switcher= Switcher(self)
    #
    def initAudioInput(self):
        self.audioFile = DS.DataSet.getData('source_audio')
        if not self.audioFile:
            return self
        file   = WV.open(self.audioFile, 'rb')
        frames = file.readframes(file.getnframes())
        self.ndataInput = NP.fromstring(frames, dtype = (NP.int8, NP.int16)[file.getsampwidth() - 1])
        self.ndataInput.shape = [-1, file.getnchannels()]
        self.ndataInputSamplerate = file.getframerate()
        self.ndataFrames          = file.getnframes()
        #
        self.player   = Player(self.outputDevice)
        self.recorder = Recorder(self.inputDevice, self.ndataFrames, self.ndataInputSamplerate)
        self.ndataOutputSamplerate = self.recorder.samplerate
        #
        ST.setSpeakerVol(0.5, 0.5)
        return self
    #
    def test(self, device):
        currentMode = DS.DataSet.getData('current_mode')
        for i in (0, 1):
            if not self.openSwitch(device, i):
                self.master.doLog(u'切换到设备:[%s%s]失败' % (device['name'], (u'左声道', u'右声道')[i]))
            self.master.doLog(u'%s测试' % (u'左声道', u'右声道')[i])
            self.player.play(self.ndataInput, self.ndataInputSamplerate)
            self.recorder.rec()
            self.player.wait()
            self.recorder.wait()
            self.master.doLog(u'%s测试结束' % (u'左声道', u'右声道')[i])
            recData = self.recorder.getData()
            #self.master.doLog(u'回放')
            #self.player.play(recData, self.ndataOutputSamplerate)
            #self.player.wait()
            fp = WV.open(r'D:\playback.wav', 'wb')
            fp.setnchannels(recData.shape[1])
            fp.setnframes(recData.shape[0])
            fp.setsampwidth(({'int8' : 1, 'int16' : 2}[recData.dtype.name]))
            fp.setframerate(self.ndataOutputSamplerate)
            fp.writeframes(recData.tostring())
            self.master.doLog(u'回放结束')
            inputData = NP.array(tuple(e[0] for e in recData))
            outputData= NP.array(tuple(e[1] for e in recData))
            inputKey = ('::'.join((str(device['name']), str(device['value']), str(self.currentDeviceIndex))), currentMode, i, 0)
            outputKey= ('::'.join((str(device['name']), str(device['value']), str(self.currentDeviceIndex))), currentMode, i, 1)
            DS.DataSet.setData(inputKey, inputData)
            DS.DataSet.setData(outputKey, outputData)
            self.master.doLog(u'开始绘图')
            input = inputData
            output= outputData
            #input = NP.array(tuple(e[0] for e in self.ndataInput))
            #output= NP.array(tuple(e[1] for e in self.ndataInput))
            self.plotter.draw(input, output, device['name'], self.currentDeviceIndex, 'r')
            self.master.doLog(u'绘图完成')
            self.currentDeviceIndex += 1
        return self
    #
    def saveFigure(self, path):
        self.plotter.saveFigure(path)
        return self
    #
    def doPlot(self):
        pass
    #
    def openSwitch(self, device, channel):
        name = device['name'].replace(' ', '_')
        switchConfig = DS.DataSet.getData(('switch_mask', name))
        return hasattr(self, 'switcher') and self.switcher.open(switchConfig[channel])
    #
    def end(self):
        if hasattr(self, 'switcher'):
            self.switcher.serialCOM.close()
        return self
#
if __name__ == '__main__':
    fp = r'D:\bibi.wav'
    file = WV.open(fp, 'rb')
    frames = file.readframes(file.getnframes())
    origin = NP.fromstring(frames, dtype = (NP.int8, NP.int16)[file.getsampwidth() - 1])
    ndata = NP.fromstring(frames, dtype = (NP.int8, NP.int16)[file.getsampwidth() - 1])
    ndata.shape = [-1, file.getnchannels()]
    device = SD.default.device[1]
    player = Player(device)
    player.play(ndata, file.getframerate())
    #
    device = SD.default.device[0]
    recorder = Recorder(device, file.getnframes())
    recorder.rec()
    player.wait()
    recorder.wait()
    player.play(recorder.getData(), file.getframerate())
    import time as TM
    TM.sleep(5)
    print 'Done'