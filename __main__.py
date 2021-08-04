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
from   PyQt5.QtGui      import QPixmap, QKeySequence
from   PyQt5.QtCore     import Qt

from   PIL              import Image
from   PIL.ImageQt      import ImageQt


class App(QMainWindow):
    '''Main application.'''
    
    def __init__(self, root, robot, *args, **kwargs):
        '''Initialise the application.'''
           
        super().__init__()
        self.root                         = root
        self.setWindowTitle('Cozmo Mars')
        
        # Setup robot properties
        self.robot                        = robot
        self.speed                        = 100 # mm/s
        self.headSpeed                    = 0.3 # rad/s
        self.liftSpeed                    = 1 # rad/s
        self.factor                       = 2
        self.direction                    = []
        robot.camera.color_image_enabled  = True
        robot.camera.image_stream_enabled = True
        robot.add_event_handler(cozmo.world.EvtNewCameraImage, self._getImage)
        
        # Delay to add to Cozmo 
        self.delays                       = {'Mars'  : 2.5,
                                             'Venus' : 1,
                                             'Lune'  : 0
                                            }
        
        # Window
        self.win            = QWidget()
        self.layoutWin      = QGridLayout()
        
        # Widgets
        self.label = QLabel()
        
        self.combobox = QComboBox()
        self.combobox.keyPressEvent = self.keyPressEvent
        self.combobox.insertItem(0, 'Lune')
        self.combobox.insertItem(1, 'Venus')
        self.combobox.insertItem(2, 'Mars')
        #self.combobox.clicked.connect(self.updateDelay)
        
        self.spinbox  = QDoubleSpinBox()
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
         
    
    ##############################
    #       Robot handling       #
    ##############################
    
    def _getImage(self, event, **kwargs):
        '''Get an image from the Cozmo event loop and show it on screen.'''
        
        image      = kwargs['image'].raw_image
        image.thumbnail((854, 480), Image.ANTIALIAS)
        self.image = ImageQt(image)
        pixmap     = QPixmap.fromImage(self.image).scaled(854, 480)
        self.label.setPixmap(pixmap)
        return
    
    def _moveBack(self, *args, **kwargs):
        '''Move the robot backward.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed, -self.speed)
        return
    
    def _moveBackLeft(self, *args, **kwargs):
        '''Move the robot to the back left.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed, -self.speed*self.factor)
        return
    
    def _moveBackRight(self, *args, **kwargs):
        '''Move the robot to the back right.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed*self.factor, -self.speed)
        return
    
    def _moveFront(self, *args, **kwargs):
        '''Move the robot frontward.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed, self.speed)
        return
    
    def _moveFrontLeft(self, *args, **kwargs):
        '''Move the robot to the front left.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed, self.speed*self.factor)
        return
    
    def _moveFrontRight(self, *args, **kwargs):
        '''Move the robot to the front right.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed*self.factor, self.speed)
        return
    
    def _moveHeadDown(self, *args, **kwargs):
        '''Move the head down.'''
        
        time.sleep(self.delay)
        self.robot.move_head(-self.headSpeed)
        return
    
    def _moveHeadUp(self, *args, **kwargs):
        '''Move the head up.'''
        
        time.sleep(self.delay)
        self.robot.move_head(self.headSpeed)
        return
    
    def _moveLeft(self, *args, **kwargs):
        '''Turn the robot to the left.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed, self.speed)
        return
    
    def _moveLiftDown(self, *args, **kwargs):
        '''Move the lift down.'''
        
        time.sleep(self.delay)
        self.robot.move_lift(-self.liftSpeed)
        return
    
    def _moveLiftUp(self, *args, **kwargs):
        '''Move the lift up.'''
        
        time.sleep(self.delay)
        self.robot.move_lift(self.liftSpeed)
        return
    
    def _moveRight(self, *args, **kwargs):
        '''Turn the robot to the right.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed, -self.speed)
        return
    
    def _stop(self, *args, **kwargs):
        '''Stop the robot.'''
        
        self.robot.stop_all_motors()
        return
    
    def _stopHead(self, *args, **kwargs):
        '''Stop moving the head.'''

        self.robot.move_head(0)
        return
    
    def _stopLift(self, *args, **kwargs):
        '''Stop moving the lift.'''

        self.robot.move_lift(0)
        return
        
    
    ############################
    #       Key handling       #
    ############################
        
    def keyReleaseEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Stop the robot.'''
        
        key = eventQKeyEvent.key()
        
        if key == Qt.Key_Up and not eventQKeyEvent.isAutoRepeat():
            
            self.direction.remove('front')
            
            if 'left' in self.direction:
                self._moveLeft()
            elif 'right' in self.direction:
                self._moveRight()
            else:
                self._stop()
                
        elif key == Qt.Key_Down and not eventQKeyEvent.isAutoRepeat():
            
            self.direction.remove('back')
            
            if 'left' in self.direction:
                self._moveLeft()
            elif 'right' in self.direction:
                self._moveRight()
            else:
                self._stop()
                
        elif key == Qt.Key_Left and not eventQKeyEvent.isAutoRepeat():
            
            self.direction.remove('left')
            
            if 'front' in self.direction:
                self._moveFront()
            elif 'back' in self.direction:
                self._moveBack()
            else:
                self._stop()
                
        elif key == Qt.Key_Right and not eventQKeyEvent.isAutoRepeat():
            
            self.direction.remove('right')
            
            if 'front' in self.direction:
                self._moveFront()
            elif 'back' in self.direction:
                self._moveBack()
            else:
                self._stop()
                
        elif key in [Qt.Key_Z, Qt.Key_S] and not eventQKeyEvent.isAutoRepeat():
                
            self._stopHead()
                
        elif key in [Qt.Key_P, Qt.Key_M] and not eventQKeyEvent.isAutoRepeat():
            
            self._stopLift()
            
            
        return

    
    def keyPressEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Move the robot in a direction.'''
    
        key = eventQKeyEvent.key()
        
        try:
            if key == Qt.Key_Up and not eventQKeyEvent.isAutoRepeat():
                
                self.direction.append('front')
                
                if 'left' in self.direction:
                    self._moveFrontLeft()
                elif 'right' in self.direction:
                    self._moveFrontRight()
                else:
                    self._moveFront()
                    
            elif key == Qt.Key_Down and not eventQKeyEvent.isAutoRepeat():
                
                self.direction.append('back')
                
                if 'left' in self.direction:
                    self._moveBackLeft()
                elif 'right' in self.direction:
                    self._moveBackRight()
                else:
                    self._moveBack()
                
            elif key == Qt.Key_Left and not eventQKeyEvent.isAutoRepeat():
                
                self.direction.append('left')
                
                if 'front' in self.direction:
                    self._moveFrontLeft()
                elif 'back' in self.direction:
                    self._moveBackLeft()
                else:
                    self._moveLeft()
                    
            elif key == Qt.Key_Right and not eventQKeyEvent.isAutoRepeat():
                
                self.direction.append('right')
                
                if 'front' in self.direction:
                    self._moveFrontRight()
                elif 'back' in self.direction:
                    self._moveBackRight()
                else:
                    self._moveRight()
                    
            elif key == Qt.Key_Z and not eventQKeyEvent.isAutoRepeat():
                
                self._moveHeadUp()
                
            elif key == Qt.Key_S and not eventQKeyEvent.isAutoRepeat():
                
                self._moveHeadDown()
                
            elif key == Qt.Key_P and not eventQKeyEvent.isAutoRepeat():
            
                self._moveLiftUp()

            elif key == Qt.Key_M and not eventQKeyEvent.isAutoRepeat():
            
                self._moveLiftDown()

        except RobotBusy:
            pass
    
        return


    #################################
    #         Miscellaneous         #
    #################################
    
    @property
    def delay(self, *args, **kwargs):
        '''Get the current delay to apply to the robot.'''
        
        text = self.combobox.currentText()
        if text in self.delays:
            return self.delays[text]
        else:
            print('Error: no delay %s found in delays list %s.' %(text, self.delays))
        
        return 0
      
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
     
        
    def 
     
    
     
def startGUI(robot, *args, **kwargs):
    root   = QApplication(sys.argv)
    app    = App(root, robot)
    sys.exit(root.exec_())

if __name__ == '__main__':
    cozmo.run_program(startGUI)
     
   