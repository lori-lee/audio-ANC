#!/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as GUI
import widget as WG
import serial.tools.list_ports as SLP

class SelectEvent:
    ET_OPTION_CLICKED = 'clicked'
    ET_OPTION_CHANGED = 'changed'
#
class Select(WG.Widget):
    def __init__(self, master, options, *argvs, **kwargvs):
        WG.Widget.__init__(self, master, options, *argvs, **kwargvs)
        self.widget = GUI.Listbox(master.getWidget(), width = 20, height = 1, highlightcolor = 'blue')
        self.options= tuple(options)
        self.currentSelection = (self.options[0], 0)
        for i in range(0, len(options)):
            self.widget.insert(i, options[i])
        font = self.getParamValue('font', u'仿宋 -18', **kwargvs)
        self.widget.config(width = 20, height = 1, font = font)
        x = self.getParamValue('x', 10, **kwargvs)
        y = self.getParamValue('y', 10, **kwargvs)
        self.widget.place(x = x, y = y)
        self.eventHandle = self.getParamValue('callback', None, **kwargvs)
        self.widget.bind('<Button-1>', self.clickHandle)
        self.widget.bind('<Motion>', self.motionHandle)
    #
    def clickHandle(self, ev):
        index = ev.widget.nearest(ev.y)
        if callable(self.eventHandle):
            self.eventHandle({'type' : SelectEvent.ET_OPTION_CLICKED, 'value' : self.options[index], 'index' : index})
            if index != self.currentSelection[0]:
                self.eventHandle({'type' : SelectEvent.ET_OPTION_CHANGED, 'value' : self.options[index], 'index' : index})
        self.currentOptions = (self.options[index], index)
        if 1 == ev.widget['height']:
            ev.widget['height'] = ev.widget.size()
        else:
            ev.widget['height'] = 1
            ev.widget.select_set(index)
            ev.widget.activate(index)
            param = (index,)
            ev.widget.after(100, ev.widget.see, (index,))
    #
    def motionHandle(self, ev):
        index = ev.widget.nearest(ev.y)
        ev.widget.activate(index)
        ev.widget.see(index)
        for i in range(0, ev.widget.size() - 1):
            ev.widget.selection_clear(i)
        ev.widget.select_set(index)
#
if __name__ == '__main__':
    class TestClass(WG.Widget):
        def __init__(self, master, *argvs, **kwargvs):
            WG.Widget.__init__(self, master, *argvs, **kwargvs)
            self.root   = GUI.Tk()
            self.widget = GUI.Frame(self.root, width = 400, height = 400, bg = 'white')
            self.widget.place(x = 0, y = 0)
            options = []
            for i in range(1, 7):
                options.append(u'选项--%d' % i)
            select = Select(self, options)
            self.root.mainloop()
    test = TestClass(None)