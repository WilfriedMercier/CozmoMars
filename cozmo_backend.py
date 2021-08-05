#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 14:18:39 2021

@author: Wilfried Mercier - IRAP

Implement actions done with cozmo using QThreads
"""

import time
import cozmo

from   PyQt5.QtGui  import QPixmap
from   PyQt5.QtCore import QObject

from   PIL          import Image
from   PIL.ImageQt  import ImageQt

class Worker(QObject):
    
    def __init__(self, parent, robot, speed, headSpeed, liftSpeed, factor, *args, **kwargs):
        '''
        Init method.
        
        :param QMainWindow parent: main window containing this worker
        :param robot: Cozmo robot object
        :param float speed: velocity in mm/s
        :param float headSpeed: head velocity in rad/s
        :param float liftSpeed: lift velocity in rad/s
        :param float factor: factor to apply to the robot velocity when turning left or right while moving
        '''
        
        self.parent                            = parent
        super().__init__()
        
        # Setup robot properties
        self.robot                             = robot
        self.speed                             = speed
        self.headSpeed                         = headSpeed
        self.liftSpeed                         = liftSpeed
        self.factor                            = factor
        
        self.robot.camera.color_image_enabled  = True
        self.robot.camera.image_stream_enabled = True
        self.robot.add_event_handler(cozmo.world.EvtNewCameraImage, self.getImage)
        
        # Which method to apply
        self.method                            = None
        self.newMethod                         = None

    def run(self, *args, **kwargs):
        """Run method."""

        while True:
            
            #If method changed, we update and apply it
            if self.newMethod != self.method:
                self._updateMethod()
                
                try:
                    getattr(self, self.method)(*args, **kwargs)
            
                except AttributeError:
                    print('No method %s found for Cozmo.' %self.method)
                    
            time.sleep(0.1)
            
        return
    
    @property
    def delay(self, *args, **kwargs):
        '''Reimplement parent delay attribute.'''
        
        return self.parent.delay
    
    def _updateMethod(self, *args, **kwargs):
        '''Update the method value with the new one.'''
        
        self.method = self.newMethod
        return
    
    
    ##############################
    #       Robot handling       #
    ##############################
    
    def getImage(self, event, **kwargs):
        '''Get an image from the Cozmo event loop and show it on screen.'''
        
        image        = kwargs['image'].raw_image
        image.thumbnail((854, 480), Image.ANTIALIAS)
        
        self.parent.image = ImageQt(image)
        pixmap       = QPixmap.fromImage(self.parent.image).scaled(854, 480)
        
        self.parent.label.setPixmap(pixmap)
        return
    
    def moveBack(self, *args, **kwargs):
        '''Move the robot backward.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed, -self.speed)
        return
    
    def moveBackLeft(self, *args, **kwargs):
        '''Move the robot to the back left.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed, -self.speed*self.factor)
        return
    
    def moveBackRight(self, *args, **kwargs):
        '''Move the robot to the back right.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(-self.speed*self.factor, -self.speed)
        return
    
    def moveFront(self, *args, **kwargs):
        '''Move the robot frontward.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed, self.speed)
        return
    
    def moveFrontLeft(self, *args, **kwargs):
        '''Move the robot to the front left.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed, self.speed*self.factor)
        return
    
    def moveFrontRight(self, *args, **kwargs):
        '''Move the robot to the front right.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed*self.factor, self.speed)
        return
    
    def moveHeadDown(self, *args, **kwargs):
        '''Move the head down.'''
        
        time.sleep(self.delay)
        self.robot.move_head(-self.headSpeed)
        return
    
    def moveHeadUp(self, *args, **kwargs):
        '''Move the head up.'''
        
        time.sleep(self.delay)
        self.robot.move_head(self.headSpeed)
        return
    
    def moveLeft(self, *args, **kwargs):
        '''Turn the robot to the left.'''
        
        print('Left1')
        time.sleep(self.delay)
        print('Left2')
        self.robot.drive_wheel_motors(-self.speed, self.speed)
        return
    
    def moveLiftDown(self, *args, **kwargs):
        '''Move the lift down.'''
        
        time.sleep(self.delay)
        self.robot.move_lift(-self.liftSpeed)
        return
    
    def moveLiftUp(self, *args, **kwargs):
        '''Move the lift up.'''
        
        time.sleep(self.delay)
        self.robot.move_lift(self.liftSpeed)
        return
    
    def moveRight(self, *args, **kwargs):
        '''Turn the robot to the right.'''
        
        time.sleep(self.delay)
        self.robot.drive_wheel_motors(self.speed, -self.speed)
        return
    
    def stop(self, *args, **kwargs):
        '''Stop the robot.'''
        
        print('Stop1')
        time.sleep(self.delay)
        print('Stop2')
        self.robot.stop_all_motors()
        return
    
    def stopHead(self, *args, **kwargs):
        '''Stop moving the head.'''

        time.sleep(self.delay)
        self.robot.move_head(0)
        return
    
    def stopLift(self, *args, **kwargs):
        '''Stop moving the lift.'''

        time.sleep(self.delay)
        self.robot.move_lift(0)
        return