#!/bin/env python
# -*- coding: utf-8 -*-
import ctypes as CT
import ctypes.wintypes as WT
import subject as SJ
import observers as OBS

class OPENFILENAME(CT.Structure):
    _fields_ = [
        ('lStructSize', WT.DWORD),
        ('hwndOwner',   WT.HWND),
        ('hInstance',   WT.HINSTANCE),
        ('lpstrFilter', WT.LPCWSTR),
        ('lpstrCustomFilter', WT.LPWSTR),
        ('nMaxCustFilter', WT.DWORD),
        ('nFilterIndex',   WT.DWORD),
        ('lpstrFile',      WT.LPWSTR),
        ('nMaxFile',       WT.DWORD),
        ('lpstrFileTitle', WT.LPWSTR),
        ('nMaxFileTitle',  WT.DWORD),
        ('lpstrInitialDir',WT.LPCWSTR),
        ('lpstrTitle',     WT.LPCWSTR),
        ('Flags',          WT.DWORD),
        ('nFileOffset',    WT.WORD),
        ('nFileExtension', WT.WORD),
        ('lpstrDefExt',    WT.LPCWSTR),
        ('lCustData',      WT.DWORD),
        ('lpfnHook',       WT.LPVOID),
        ('lpTemplateName', WT.LPCWSTR),
    ]
#
class OpenFileDlgStates:
    ST_OPENFILE_OK   = 'open_file_success'
    ST_OPENFILE_FAIL = 'open_file_failed'
#
class OpenFileDlg(SJ.Subject):
    #
    def __init__(self, *argsv, **kwargsv):
        SJ.Subject.__init__(self, *argsv, **kwargsv)
        prototype = CT.WINFUNCTYPE(WT.BOOL, CT.POINTER(OPENFILENAME))
        paramDecl = (3, 'lpofn'),
        self.winAPI = prototype(('GetOpenFileNameW', CT.windll.comdlg32), paramDecl)
    #
    def show(self):
        lpofn = OPENFILENAME()
        fileNameBuff = CT.create_unicode_buffer(0, 256);
        lpofn.lStructSize = CT.sizeof(OPENFILENAME)
        lpofn.lpstrFilter = self.getParamValue('filter', u'所有文件\0*.*\0文本文件\0*.txt\0', **self.kwargsv)
        lpofn.lpstrFile   = fileNameBuff.value
        lpofn.nMaxFile    = 255
        lpofn.lpstrInitialDir = self.getParamValue('directory', u'D:\\', **self.kwargsv)
        lpofn.lpstrTitle = self.getParamValue('title', u'请选择要打开的文件', **self.kwargsv)
        lpofn.Flags = 0x80000 | 0x1000
        if self.winAPI(CT.pointer(lpofn)):
            self.setState(OpenFileDlgStates.ST_OPENFILE_OK, file = lpofn.lpstrFile)
            return lpofn.lpstrFile
        else:
            self.setState(OpenFileDlgStates.ST_OPENFILE_FAIL)
            return False
#
class MessageBox(SJ.Subject):
    def __init__(self, *argsv, **kwargsv):
        SJ.Subject.__init__(self, *argsv, **kwargsv)
        prototype = CT.WINFUNCTYPE(CT.c_int, WT.HWND, WT.LPCWSTR, WT.LPCWSTR, WT.UINT)
        paramDecl = (1, 'hWnd', None), (1, 'lpText', ''), (1, 'lpCaption', ''), (1, 'uType', 0)
        self.winAPI = prototype(('MessageBoxW', CT.windll.user32), paramDecl)
    #
    def show(self):
        lpText = self.kwargsv.get('text') if self.kwargsv.has_key('text') else u'这里是文本消息'
        lpTitle= self.kwargsv.get('title') if self.kwargsv.has_key('title') else ''
        self.winAPI(lpText = lpText, lpCaption = lpTitle)
        return self
    #

def setSpeakerVol(left, right):
        winmm = CT.windll.winmm
        def normVol(vol):
            if vol <= 0:
                vol = 0
            elif vol < 1 or not cmp(type(vol), type(0.0)):
                vol = int(vol * 0xFFFF)
            vol = min(0xFFFF, vol)
            return vol
        #
        left = normVol(left)
        right= normVol(right)
        winmm.waveOutSetVolume(None, left + (right << 16))
#
if __name__ == '__main__':
    dlg = OpenFileDlg(filter = u'Python文件\0*.py;*.pyd;*.pyc\0\0')
    #dlg.show()
    box = MessageBox(text = u'hello world', title = u'我是标题')
    #box.show()
    setSpeakerVol(0, 0)
####################################################
#OFN_ALLOWMULTISELECT    (0x200)
#OFN_CREATEPROMPT    (0x2000)
#OFN_ENABLEHOOK  (0x20)
#OFN_ENABLETEMPLATE  (0x40)
#OFN_ENABLETEMPLATEHANDLE    (0x80)
#OFN_EXPLORER    (0x80000)
#OFN_EXTENSIONDIFFERENT  (0x400)
#OFN_FILEMUSTEXIST   (0x1000)
#OFN_HIDEREADONLY    (0x4)
#OFN_LONGNAMES   (0x200000)
#OFN_NOCHANGEDIR (0x8)
#OFN_NODEREFERENCELINKS  (0x100000)
#OFN_NOLONGNAMES (0x40000)
#OFN_NONETWORKBUTTON (0x20000)
#OFN_NOREADONLYRETURN    (0x8000)
#OFN_NOTESTFILECREATE    (0x10000)
#OFN_NOVALIDATE  (0x100)
#OFN_OVERWRITEPROMPT (0x2)
#OFN_PATHMUSTEXIST   (0x800)
#OFN_READONLY    (0x1)
#OFN_SHAREAWARE  (0x4000)
#OFN_SHOWHELP    (0x10)
#/* SHAREVISTRING message */
#OFN_SHAREFALLTHROUGH    (0x2)
#OFN_SHARENOWARN (0x1)
#OFN_SHAREWARN   (0)
#############################################################
#MB_ABORTRETRYIGNORE        0x00000002L
#MB_CANCELTRYCONTINUE       0x00000006L
#MB_HELP                    0x00004000L
#MB_OK                      0x00000000L
#MB_OKCANCEL                0x00000001L
#MB_RETRYCANCEL             0x00000005L
#MB_YESNO                   0x00000004L
#MB_YESNOCANCEL             0x00000003L
