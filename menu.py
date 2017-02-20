#!/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as GUI
import command as CMD
import subject as SJ
import widget as WG

class MenuStates:
    ST_MENU_CLICKED = 'menu_clicked'
#
class MenuWidget(WG.Widget):
    def __init__(self, master):
        SJ.Subject.__init__(self)
        self.name   = 'menu_widget'
        self.master = master
        self.widget = GUI.Menu(self.master.getWidget())
#
class MenuIdentities:
    MN_WIN_TEST     = 'win_test'
    MN_WIN_DEVICES  = 'device_chosen'
    MN_LINE_SEP     = 'win_separator'
    MN_EXIT         = 'win_exit'
    MN_BURN_PCB     = 'burn_file'
    MN_AUDIO_FILE   = 'input_audio_file'
    MN_HELP_USAGE   = 'help_usage'
    MN_HELP_ABOUT   = 'help_about_me'
#
class ApplicationMenu(MenuWidget):
    def __init__(self, master):
        MenuWidget.__init__(self, master)
        self.name = 'app_menu'
        self.init()
    #
    def init(self):
        #
        menuList = (
            {'name' : u'界面',
                'children' : (
                    {'id' : MenuIdentities.MN_WIN_TEST, 'name' : u'测试'},
                    {'id' : MenuIdentities.MN_WIN_DEVICES, 'name' : u'设备'},
                    {'id' : MenuIdentities.MN_LINE_SEP, 'name' : ''},
                    {'id' : MenuIdentities.MN_EXIT, 'name' : u'退出'}
                )
             },
            {'name' : u'配置',
                'children' : (
                    {'id' : MenuIdentities.MN_BURN_PCB, 'name' : u'烧写PCB'},
                    {'id' : MenuIdentities.MN_AUDIO_FILE, 'name' : u'导入音频文件'},
                )
             },
            {'name' : u'帮助',
                 'children': (
                     {'id': MenuIdentities.MN_HELP_USAGE, 'name': u'使用方法'},
                     {'id': MenuIdentities.MN_HELP_ABOUT, 'name': u'关于'},
                 )
             },
        )
        for menuInfo in menuList:
            menu = GUI.Menu(self.widget, tearoff = 0)
            for subMenuInfo in menuInfo.get('children'):
                if subMenuInfo.get('name'):
                    menu.add_command(
                        label = subMenuInfo.get('name'),
                        command = CMD.Command(self.menuClick, id = subMenuInfo.get('id')),
                    )
                else:
                    menu.add_separator()
            self.widget.add_cascade(label = menuInfo.get('name'), menu = menu)
        self.master.getWidget().config(menu = self.widget)
        return self

    def menuClick(self, *argsv, **kwargsv):
        self.setState(MenuStates.ST_MENU_CLICKED, *argsv, **kwargsv)
        return self

if __name__ == '__main__':
    import observer as OB
    class TestOB(OB.Observer):
        def update(self, **kwargsv):
            print 'hello subject', kwargsv
            return self
    #
    class Base:
        def __init__(self):
            self.widget = GUI.Tk()
            TestOB(ApplicationMenu(self))
            self.widget.mainloop()
        def getWidget(self):
            return self.widget
    app = Base()
