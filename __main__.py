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


import time
import sys

import cozmo
from   cozmo.util       import distance_mm, speed_mmps, degrees
from   cozmo.exceptions import RobotBusy

from   PyQt5.QtWidgets  import QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QShortcut, QComboBox, QDoubleSpinBox
from   PyQt5.QtGui      import QKeySequence
from   PyQt5.QtCore     import Qt, QThread, QTimer

from   PIL              import Image
from   PIL.ImageQt      import ImageQt

from   cozmo_backend    import Worker


class App(QMainWindow):
    '''Main application.'''
    
    def __init__(self, root, robot, *args, **kwargs):
        '''Initialise the application.'''
           
        super().__init__()
        self.root                         = root
        self.setWindowTitle('Cozmo Mars')
        
        # Setup robot properties
        self.robot                        = Worker(self, robot, 100, 0.3, 1, 2)
        self.direction                    = []
        self.pause                        = False
        
        # Delay to add to Cozmo 
        self.delays                       = {'Mars'  : 2.5,
                                             'Venus' : 1,
                                             'Lune'  : 0
                                            }
        
        # Window
        self.win                          = QWidget()
        self.layoutWin                    = QGridLayout()
        
        # Widgets
        
        self.nameLabel1                   = QLabel('Astre de destination')
        self.nameLabel2                   = QLabel('Délai')
        
        self.label                        = QLabel()
        self.label.mousePressEvent        = self.labelConnect
        
        self.combobox                     = QComboBox()
        self.combobox.keyPressEvent       = self.keyPressEvent
        self.combobox.insertItem(0, 'Lune')
        self.combobox.insertItem(1, 'Venus')
        self.combobox.insertItem(2, 'Mars')
        self.combobox.insertItem(3, 'Manuel')
        self.combobox.activated.connect(self.updateDelay)
        
        self.spinbox                      = QDoubleSpinBox()
        self.spinbox.savedKeyPressEvent   = self.spinbox.keyPressEvent
        self.spinbox.keyPressEvent        = self.spinboxPressEvent
        self.spinbox.setReadOnly(True)
        self.spinbox.setSuffix(' secondes')
        self.spinbox.setDecimals(1)
        self.spinbox.setMinimum(0)
        self.spinbox.setValue(self.delays['Lune'])

        # Setup layout    
        self.layoutWin.addWidget(self.nameLabel1, 1, 1)
        self.layoutWin.addWidget(self.nameLabel2, 1, 2)
        self.layoutWin.addWidget(self.combobox,   2, 1)
        self.layoutWin.addWidget(self.spinbox,    2, 2)
        self.layoutWin.addWidget(self.label,      3, 1, 1, 2)
        
        self.win.setLayout(self.layoutWin)
        
        # Show application
        self.setCentralWidget(self.win)
        self.show()
        #self.centre()
        self.resumeCozmo()
        self.robot.robot.say_text("Allez ! On va bien samuser !", voice_pitch=1) #, play_excited_animation=True)
        #self.robot.robot.say_text('', play_excited_animation=True)
        
        
    ################################################
    #       Pause and resume Cozmo functions       #
    ################################################
    
    def labelConnect(self, *args, **kwargs):
        '''Slot related to clicking on the main label.'''
        
        if self.pause:
            self.resumeCozmo()
        else:
            self.pauseCozmo()
            
        return
    
    def pauseCozmo(self, *args, **kwargs):
        '''Pause Cozmo autonomous behaviour.'''
        
        self.robot.stop()
        self.robot.stopHead()
        self.robot.stopLift()
        self.robot.stopAnimate()
        self.label.setStyleSheet("border: 3px solid red")
        self.pause = True
        return
    
    def resumeCozmo(self, *args, **kwargs):
        '''Resume Cozmo autonomous behaviour.'''
        
        delay = int(self.delay*1000)
        QTimer.singleShot(delay + self.robot.behaviourDelay, self.robot.animate)
        self.label.setStyleSheet("border: 3px solid green")
        self.pause = False
        return
    
    
    ############################
    #       Key handling       #
    ############################
    
    def activateCozmo(self, action):
        '''
        Activate Cozmo with the given action.
        
        :param str action: method to apply to the worker
        '''
        
        if not self.pause:
            delay = int(self.delay*1000)
            QTimer.singleShot(delay, getattr(self.robot, action))
            
            if 'stop' in action:
                QTimer.singleShot(delay + self.robot.behaviourDelay, self.robot.animate)
            
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
            
            # Update behaviour time when any key is pressed
            self.robot.setBehaviourTime()
            
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
     
   