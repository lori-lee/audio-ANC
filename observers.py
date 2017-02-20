#!/bin/env python
# -*- coding: utf-8 -*-
import sounddevice as SD
import thread as TH

class Player:
    def __init__(self, device, ndata, samplerate, blocksize = None):
        self.device = device
        self.ndata  = ndata
        self.samplerate = samplerate
        if blocksize == None:
            self.blocksize = self.ndata.shape[0]
        else:
            self.blocksize = blocksize
        self.currentFrame = 0
        self.frames = ndata.shape[0]
        self.playLock = TH.allocate_lock()
    #
    def play(self):
        self.outputStream = SD.OutputStream(
            device = self.device,
            samplerate = self.samplerate,
            channels   = self.ndata.shape[1],
            dtype = self.ndata.dtype.name,
            callback = self.streamFeeder,
        )
        self.playLock.acquire()
        self.outputStream.start()
        return self
    #
    def streamFeeder(self, outdata, frames, time, status):
        if self.currentFrame >= self.frames:#Game over
            self.outputStream.close()
            if self.playLock.locked():
                self.playLock.release()
        #print 'Playing: %d~%d, frames: %d, time: %s' % (self.currentFrame, self.currentFrame + self.blocksize, frames, time)
        #print 'Outdata len:%d' % len(outdata)
        self.blocksize = min(self.frames - self.currentFrame, len(outdata))
        outdata[:self.blocksize] = self.ndata[self.currentFrame : self.currentFrame + self.blocksize]
        outdata[self.blocksize:] = 0
        self.currentFrame += self.blocksize
    #
    def isDone(self):
        return not self.playLock.locked()
    #
    def wait(self):
        self.playLock.acquire()
        self.playLock.release()
        return self