#!/bin/env python
# -*- coding: utf-8 -*-
import sounddevice as SD
import numpy as NP
import thread as TH

class Recorder:
    def __init__(self, device, frames):
        self.device = device
        deviceInfo  = SD.query_devices(device)
        self.samplerate = deviceInfo.get('default_samplerate')
        self.channels   = deviceInfo.get('max_input_channels')
        self.ndata  = NP.empty((frames, self.channels), dtype = NP.int16)
        self.frames = frames
        self.currentFrame = 0
        self.recLock = TH.allocate_lock()
    #
    def rec(self):
        self.inputStream = SD.InputStream(
            device = self.device,
            samplerate = self.samplerate,
            channels = self.channels,
            dtype = NP.dtype(NP.int16).name,
            callback = self.recFeeder,
            latency = 'low',
            prime_output_buffers_using_stream_callback = True
        )
        self.recLock.acquire()
        self.inputStream.start()
        return self
    #
    def recFeeder(self, indata, frames, time, status):
        self.blocksize = min(self.frames - self.currentFrame, len(indata))
        self.ndata[self.currentFrame : self.currentFrame + self.blocksize] = indata[:self.blocksize]
        self.currentFrame += self.blocksize
        #print 'recording: %d-%d' % (self.currentFrame - self.blocksize, self.currentFrame)
        if self.currentFrame >= self.frames:#Game over
            self.inputStream.close()
            if self.recLock.locked():
                self.recLock.release()
    #
    def getData(self, block = True):
        if block:
            self.recLock.acquire()
            self.recLock.release()
        return self.ndata