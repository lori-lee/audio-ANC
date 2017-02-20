#!/bin/env python
import subject as SJ

class Observer:
    def __init__(self, subject):
        self.statesInterested = ('*')
        if isinstance(subject, SJ.Subject):
            self.subject = subject
            self.subject.attach(self)
        else:
            raise Exception('Parameter 2 subject is not an instance of subject.Subject')
    #
    def update(self, *argsv, **kwargsv):
        return self
    #
    def getStatesInterested(self):
        return self.statesInterested