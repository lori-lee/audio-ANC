#!/bin/env python
import Tkinter as GUI
import subject as SJ
import dataset as DS

class WidgetStates:
    ST_CREATED  = 'widget_created'
    ST_DESTROY  = 'widget_destroy'
    ST_DESTROYED= 'widget_destroyed'
    #
    ST_CHILDREN_DESTROY   = 'widget_children_destroy'
    ST_CHILDREN_DESTROYED = 'widget_children_destroyed'
    #
    ST_CHILD       = 'widget_child_adding'
    ST_CHILD_ADDED = 'widget_child_added'
    #
    ST_CHILDREN_CLEAN   = 'widget_children_clean'
    ST_CHILDREN_CLEANED = 'widget_children_cleaned'
    #
class Widget(SJ.Subject):
    #
    def __init__(self, master, *argsv, **kwargsv):
        SJ.Subject.__init__(self, *argsv, **kwargsv)
        self.name   = 'base_widget'
        self.master = master
        self.widget = GUI.Frame(self.master.getWidget()) if master else None
        self.children = []
        if master:
            master.addChild(self)
        self.setState(WidgetStates.ST_CREATED)
    #
    def getWidget(self):
        return self.widget
    #
    def addChild(self, child):
        self.setState(WidgetStates.ST_CHILD, child = child)
        if isinstance(child, Widget):
            self.children.append(child)
            self.setState(WidgetStates.ST_CHILD_ADDED, child = child)
        return self
    #
    def getChildren(self):
        return self.children
    #
    def clearChildren(self):
        self.setState(WidgetStates.ST_CHILDREN_CLEAN)
        self.children = []
        self.setState(WidgetStates.ST_CHILDREN_CLEANED)
        return self
    #
    def destroyChildren(self):
        self.setState(WidgetStates.ST_CHILDREN_DESTROY)
        for child in self.children:
            child.destroy()
        self.clearChildren()
        self.setState(WidgetStates.ST_CHILDREN_DESTROYED)
        return self
    #
    def destroy(self):
        self.setState(WidgetStates.ST_DESTROY)
        self.destroyChildren()
        if self.widget and self.widget.destroy:
            self.widget.destroy()
            self.widget = None
        self.setState(WidgetStates.ST_DESTROYED)
        return self
    #
    def getMaster(self, distance = 1):
        if not distance:
            return self
        elif distance > 0:
            return None if not self.master else self.master.getMaster(distance - 1)
        else:
            return self if not self.master else self.master.getMaster(distance)
    #
    def doLog(self, message):
        self.getMaster(-1).logMutex.acquire()
        currentLog = DS.DataSet.getData('application_log')
        if not currentLog:
            currentLog = []
        currentLog.append(message)
        DS.DataSet.setData('application_log', currentLog)
        self.getMaster(-1).logMutex.release()
        if hasattr(self, 'displayLog') and callable(self.displayLog):
            self.displayLog()
        return self