#!/bin/env python
import observer as OB
import dataset as DS
import thread as TH

class Subject:
    def __init__(self, *argsv, **kwargsv):
        self.name   = 'base_subject'
        self.argsv  = argsv
        self.kwargsv= kwargsv
        self.state  = None
        self.observerSet = []
        #
        self.logMutext = TH.allocate_lock()
    #
    def setState(self, state, *argsv, **kwargsv):
        self.state = state
        self.notify(*argsv, **kwargsv)
        return self
    #
    def getState(self):
        return self.state
    #
    def notify(self, *argsv, **kwargsv):
        for ob in self.observerSet:
            if (self.state in ob.getStatesInterested()) or ('*' in ob.getStatesInterested()):
                ob.update(*argsv, **kwargsv)
        return self
    #
    def attach(self, observer):
        if isinstance(observer, OB.Observer):
            self.observerSet.append(observer)
        else:
            raise Exception('Parameter 2 observer is not an instance of observer.Observer')
        return self
    #
    def getParamValue(self, key, default, **kwargsv):
        return kwargsv.get(key) if kwargsv.has_key(key) else default
    #