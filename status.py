#!/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as GUI

class Status:
    def __init__(self, master):
        self.widget = GUI.LableFrame(master)
        self.config(width = 20, height = 10, text = 'Progress')