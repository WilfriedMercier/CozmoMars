#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:57:39 2021

@author: Wilfried Mercier - IRAP

Simple GUI which shows Cozmo camera and allow to control with a delay supposed to mimick the delay of rovers on Mars.
"""

import asyncio
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import sys

import cozmo
from   cozmo.util       import distance_mm, speed_mmps, degrees
from   cozmo.exceptions import RobotBusy

from   PyQt5.QtWidgets  import QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QShortcut, QComboBox, QDoubleSpinBox
from   PyQt5.QtGui      import QKeySequence
from   PyQt5.QtCore     import Qt, QThread

from   PIL              import Image
from   PIL.ImageQt      import ImageQt

from   types            import MethodType

from   cozmo_backend    import Worker


class App(QMainWindow):
    '''Main application.'''
    
    def __init__(self, root, robot, *args, **kwargs):
        '''Initialise the application.'''
           
        super().__init__()
        self.root                         = root
        self.setWindowTitle('Cozmo Mars')
        
        # Setup robot properties
        self.thread                       = QThread()
        self.worker                       = Worker(self, robot, 100, 0.3, 1, 2)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        
        self.direction                    = []
        
        
        # Delay to add to Cozmo 
        self.delays                       = {'Mars'  : 2.5,
                                             'Venus' : 1,
                                             'Lune'  : 0
                                            }
        
        # Window
        self.win                          = QWidget()
        self.layoutWin                    = QGridLayout()
        
        # Widgets
        self.label = QLabel()
        
        self.combobox = QComboBox()
        self.combobox.keyPressEvent       = self.keyPressEvent
        self.combobox.insertItem(0, 'Lune')
        self.combobox.insertItem(1, 'Venus')
        self.combobox.insertItem(2, 'Mars')
        self.combobox.insertItem(3, 'Manuel')
        self.combobox.activated.connect(self.updateDelay)
        
        self.spinbox  = QDoubleSpinBox()
        self.spinbox.savedKeyPressEvent   = self.spinbox.keyPressEvent
        self.spinbox.keyPressEvent        = self.spinboxPressEvent
        self.spinbox.setReadOnly(True)
        self.spinbox.setSuffix(' secondes')
        self.spinbox.setDecimals(1)
        self.spinbox.setMinimum(0)
        self.spinbox.setValue(self.delays['Lune'])

        # Setup layout    
        self.layoutWin.addWidget(self.combobox, 1, 1)
        self.layoutWin.addWidget(self.spinbox, 1, 2)
        self.layoutWin.addWidget(self.label, 2, 1, 1, 2)
        
        self.win.setLayout(self.layoutWin)
        
        # Show application
        self.setCentralWidget(self.win)
        self.show()
        #self.centre()
    
    
    ############################
    #       Key handling       #
    ############################
    
    def activateCozmo(self, action):
        '''
        Activate Cozmo with the given action.
        
        :param str action: method to apply to the worker
        '''
        
        self.worker.newMethod = action
        
        return
        
    def keyReleaseEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Stop the robot.'''
        
        key = eventQKeyEvent.key()
        
        if key == Qt.Key_Up and not eventQKeyEvent.isAutoRepeat():
            
            self.direction.remove('front')
            
            if 'left' in self.direction:
                self.activateCozmo('moveLeft')
            elif 'right' in self.direction:
                self.activateCozmo('moveRight')
            else:
                self.activateCozmo('stop')
   
        elif key == Qt.Key_Down and not eventQKeyEvent.isAutoRepeat():
            
             self.direction.remove('back')
            
             if 'left' in self.direction:
                 self.activateCozmo('moveLeft')
             elif 'right' in self.direction:
                 self.activateCozmo('moveRight')
             else:
                 self.activateCozmo('stop')
                
        elif key == Qt.Key_Left and not eventQKeyEvent.isAutoRepeat():
            
             self.direction.remove('left')
            
             if 'front' in self.direction:
                 self.activateCozmo('moveFront')
             elif 'back' in self.direction:
                 self.activateCozmo('moveBack')
             else:
                 self.activateCozmo('stop')
                
        elif key == Qt.Key_Right and not eventQKeyEvent.isAutoRepeat():
            
             self.direction.remove('right')
            
             if 'front' in self.direction:
                 self.activateCozmo('moveFront')
             elif 'back' in self.direction:
                 self.activateCozmo('moveBack')
             else:
                 self.activateCozmo('stop')
                
        elif key in [Qt.Key_Z, Qt.Key_S] and not eventQKeyEvent.isAutoRepeat():
             self.activateCozmo('stopHead')
        elif key in [Qt.Key_P, Qt.Key_M] and not eventQKeyEvent.isAutoRepeat():
             self.activateCozmo('stopLift')

        return

    
    def keyPressEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Move the robot in a direction.'''
    
        key = eventQKeyEvent.key()
        
        try:
            if key == Qt.Key_Up and not eventQKeyEvent.isAutoRepeat():
                
                self.direction.append('front')
                
                if 'left' in self.direction:
                    self.activateCozmo('moveFrontLeft')
                elif 'right' in self.direction:
                    self.activateCozmo('moveFrontRight')
                else:
                    self.activateCozmo('moveFront')

            elif key == Qt.Key_Down and not eventQKeyEvent.isAutoRepeat():
                
                 self.direction.append('back')
                
                 if 'left' in self.direction:
                     self.activateCozmo('moveBackLeft')
                 elif 'right' in self.direction:
                     self.activateCozmo('moveBackRight')
                 else:
                     self.activateCozmo('moveBack')
                
            elif key == Qt.Key_Left and not eventQKeyEvent.isAutoRepeat():
                
                 self.direction.append('left')
                
                 if 'front' in self.direction:
                     self.activateCozmo('moveFrontLeft')
                 elif 'back' in self.direction:
                     self.activateCozmo('moveBackLeft')
                 else:
                     self.activateCozmo('moveLeft')
                    
            elif key == Qt.Key_Right and not eventQKeyEvent.isAutoRepeat():
                
                 self.direction.append('right')
                
                 if 'front' in self.direction:
                     self.activateCozmo('moveFrontRight')
                 elif 'back' in self.direction:
                     self.activateCozmo('moveBackRight')
                 else:
                     self.activateCozmo('moveRight')
                    
            elif key == Qt.Key_Z and not eventQKeyEvent.isAutoRepeat():
                 self.activateCozmo('moveHeadUp') 
            elif key == Qt.Key_S and not eventQKeyEvent.isAutoRepeat():   
                 self.activateCozmo('moveHeadDown')  
            elif key == Qt.Key_P and not eventQKeyEvent.isAutoRepeat():
                 self.activateCozmo('moveLiftUp')
            elif key == Qt.Key_M and not eventQKeyEvent.isAutoRepeat():
                 self.activateCozmo('moveLiftDown')

        except RobotBusy:
            pass
    
        return


    #################################
    #         Miscellaneous         #
    #################################
    
    @property
    def delay(self, *args, **kwargs):
        '''Get the current delay to apply to the robot.'''
        
        return self.spinbox.value()
    
    def centre(self, *args, **kwargs):
         '''Centre the window.'''
    
         frameGm     = self.frameGeometry()
         screen      = self.root.desktop().screenNumber(self.root.desktop().cursor().pos())
         centerPoint = self.root.desktop().screenGeometry(screen).center()
         centerPoint.setY(centerPoint.y())
         centerPoint.setX(centerPoint.x())
         frameGm.moveCenter(centerPoint)
         self.move(frameGm.topLeft())
         
         return
     
    def spinboxPressEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Press event actions for the spinbox widget.'''
        
        key = eventQKeyEvent.key()
        
        if key in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right, Qt.Key_Z, Qt.Key_S, Qt.Key_P, Qt.Key_M]:
            self.keyPressEvent(eventQKeyEvent, *args, **kwargs)
        else:
            self.spinbox.savedKeyPressEvent(eventQKeyEvent, *args, **kwargs)
            
        return
        
    def updateDelay(self, *args, **kwargs):
        '''Update the delay value in the spinbox.'''
        
        text = self.combobox.currentText()
        if text in self.delays:
            self.spinbox.setReadOnly(True)
            self.spinbox.setValue(self.delays[text])
        elif text == 'Manuel':
            self.spinbox.setReadOnly(False)
        else:
            print('Error, no delay could be applied with this choice.')
        
        return
     

def startGUI(robot, *args, **kwargs):
    root   = QApplication(sys.argv)
    app    = App(root, robot)
    sys.exit(root.exec_())

if __name__ == '__main__':
    cozmo.run_program(startGUI)
     
   