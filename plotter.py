#!/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as GUI
import matplotlib as MPL
import numpy as NP
import matplotlib.backends.backend_tkagg as MBTK
import matplotlib.figure as FG
import random as RD

class Plotter:
    def __init__(self, master, framerate = 44100, rows = 3, cols = 2):
        self.parent = master
        self.widget = GUI.Frame(master.getWidget())
        self.rows = rows
        self.cols = cols
        #
        self.framerate = framerate
        self.init()
    #
    def init(self):
        self.widget.config(width = 1300, height = 960, bg = 'grey')
        self.widget.place(x = 600, y = 10)
        #
        self.figure = FG.Figure(figsize = (6.5, 4.8), dpi = 200)
        #
        self.canvas = MBTK.FigureCanvasTkAgg(self.figure, master = self.widget)
        self.canvas.show()
        self.canvas.get_tk_widget().place(x = 0, y = 0)
        #
        return self
    #
    def draw(self, ya, yb, grid = 1):
        #try:
        gridRect = self.figure.add_subplot(self.rows, self.cols, grid)#, xscale = u'log')
        Pyx, freqYX = gridRect.csd(ya, yb, NFFT = self.framerate / 4, Fs = self.framerate, visible = False)
        Pxx, freqXX = gridRect.csd(ya, ya, NFFT = self.framerate / 4, Fs = self.framerate, visible = False)
        #
        gridRect.clear()
        gridRect.semilogx()
        dB = Pyx * 1.0 / Pxx
        Y  = -20 * NP.log10(abs(dB))
        winSize = 0.05
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
        help(gridRect.plot)
        gridRect.plot(freqXX, fitY + 0.5, 'r-', linewidth = 0.1, label='up bound')
        gridRect.plot(freqXX, fitY, 'b-', linewidth = 0.1, label = 'test')
        gridRect.plot(freqXX, fitY - 0.5, 'r-', linewidth = 0.1, label='lower bound')
        gridRect.legend(fancybox = False, edgecolor = 'black', loc = 0, fontsize = 3, framealpha = 0.4)
        gridRect.set_xlabel('Frequency', labelpad = -5, fontsize = 5)
        gridRect.set_ylabel('Power', labelpad = -5, fontsize = 5)
        #help(gridRect.set_xlabel)
        xmin = 10
        xmax = min(20000, max(freqXX))
        gridRect.set_xlim(xmin = xmin, xmax = xmax)
        ymin = min(Y)
        ymax = max(Y)
        gridRect.set_ylim(ymin = ymin - 0.5, ymax = ymax + 0.5)
        if ymin != ymax:
            gridRect.set_yticks(NP.linspace(ymin, ymax, 8))
        gridRect.text((xmin + xmax) * 2 / 50, (ymin - 1.5) / 50, 'text i am', bbox = dict(color = 'blue', facecolor = 'red'))
        for tick in gridRect.yaxis.get_major_ticks():
            tick.label1.set_fontsize(4)
        for tick in gridRect.xaxis.get_major_ticks():
            tick.label1.set_fontsize(4)
        gridRect.grid(color = 'g', linestyle = '-', linewidth = 0.1)
        #help(gridRect.grid)
        #help(gridRect.xaxis)
        self.canvas.show()
        #except Exception, e:
            #self.parent.appendLog(u'绘图发生异常:%s' % e.message)
        return self