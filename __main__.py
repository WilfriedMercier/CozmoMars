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
from   cozmo.util       import distance_mm, speed_mmps
from   cozmo.exceptions import RobotBusy

from   PyQt5.QtWidgets  import QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QShortcut
from   PyQt5.QtGui      import QPixmap, QKeySequence
from   PyQt5.QtCore     import Qt

from   PIL.ImageQt      import ImageQt


class App(QMainWindow):
    '''Main application.'''
    
    def __init__(self, root, robot, *args, **kwargs):
        '''Initialise the application.'''
           
        super().__init__()
        self.root               = root
        self.setWindowTitle('Cozmo Mars')
        
        # Setup robot properties
        self.robot              = robot
        self.speed              = 100 # mm/s
        robot.camera.image_stream_enabled = True
        robot.add_event_handler(cozmo.world.EvtNewCameraImage, self._getImage)
        
        # Window
        self.win            = QWidget()
        self.layoutWin      = QGridLayout()
        
        # Widgets
        self.label = QLabel()

        # Setup layout    
        self.layoutWin.addWidget(self.label, 1, 1)
        self.win.setLayout(self.layoutWin)
        
        # Setup shortcuts
        
        # Show application
        self.setCentralWidget(self.win)
        self.show()
        #self.centre()
        
    def keyReleaseEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Stop the robot.'''
        
        key = eventQKeyEvent.key()
        if key in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right] and not eventQKeyEvent.isAutoRepeat():
            self.robot.stop_all_motors()
        
    
    def keyPressEvent(self, eventQKeyEvent, *args, **kwargs):
        '''Move the robot in the given direction.'''
    
        key = eventQKeyEvent.key()
        
        try:
            if key == Qt.Key_Up and not eventQKeyEvent.isAutoRepeat():
                self.robot.drive_wheel_motors(self.speed, self.speed)
            elif key == Qt.Key_Down and not eventQKeyEvent.isAutoRepeat():
                self.robot.drive_wheel_motors(-self.speed, -self.speed)
        except RobotBusy:
            pass
    
        return
    
    def _getImage(self, event, **kwargs):
        '''Get an image from the Cozmo event loop and show it on screen.'''
        
        image      = kwargs['image'].raw_image
        self.image = ImageQt(image)
        pixmap     = QPixmap.fromImage(self.image).scaled(1280, 720)
        self.label.setPixmap(pixmap)
        return 

      
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
     
def startGUI(robot, *args, **kwargs):
    root   = QApplication(sys.argv)
    app    = App(root, robot)
    sys.exit(root.exec_())

if __name__ == '__main__':
    cozmo.run_program(startGUI)
     
   