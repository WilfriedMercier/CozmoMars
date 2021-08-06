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
from   PyQt5.QtCore import QTimer

from   PIL          import Image
from   PIL.ImageQt  import ImageQt

class Worker:
    
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
        
        # Setup robot properties
        self.robot                             = robot
        self.speed                             = speed
        self.headSpeed                         = headSpeed
        self.liftSpeed                         = liftSpeed
        self.factor                            = factor
        self.behaviour                         = False
        
        self.robot.camera.color_image_enabled  = True
        self.robot.camera.image_stream_enabled = True
        self.robot.add_event_handler(cozmo.world.EvtNewCameraImage, self.getImage)
        
        # Timer used to decide whether a behaviour must be applied or not
        self.behaviourTime                     = 0
        
        # Delay required for a behaviour to start (in ms)
        self.behaviourDelay                    = 3000
    

    def setBehaviourTime(self, *args, **kwargs):
        '''Set the behavior time.'''
        
        self.behaviourTime = time.time()
        return

    ##############################
    #       Robot freeplay       #
    ##############################
    
    def animate(self, *args, **kwargs):
        '''Animate Cozmo autonomously when idle.'''
        
        delay = (time.time() - self.behaviourTime)*1000
        if not self.behaviour and delay >= self.behaviourDelay:
            self.robot.start_freeplay_behaviors()
            self.behaviour = True
            
        return
    
    def stopAnimate(self, *args, **kwargs):
        '''Top the autonomous animation.'''
        
        if self.behaviour:
            self.robot.stop_freeplay_behaviors()
            self.behaviour = False
        
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
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(-self.speed, -self.speed)
        return
    
    def moveBackLeft(self, *args, **kwargs):
        '''Move the robot to the back left.'''
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(-self.speed, -self.speed*self.factor)
        return
    
    def moveBackRight(self, *args, **kwargs):
        '''Move the robot to the back right.'''
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(-self.speed*self.factor, -self.speed)
        return
    
    def moveFront(self, *args, **kwargs):
        '''Move the robot frontward.'''
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(self.speed, self.speed)
        return
    
    def moveFrontLeft(self, *args, **kwargs):
        '''Move the robot to the front left.'''
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(self.speed, self.speed*self.factor)
        return
    
    def moveFrontRight(self, *args, **kwargs):
        '''Move the robot to the front right.'''
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(self.speed*self.factor, self.speed)
        return
    
    def moveHeadDown(self, *args, **kwargs):
        '''Move the head down.'''
        
        self.stopAnimate()
        self.robot.move_head(-self.headSpeed)
        return
    
    def moveHeadUp(self, *args, **kwargs):
        '''Move the head up.'''
        
        self.stopAnimate()
        self.robot.move_head(self.headSpeed)
        return
    
    def moveLeft(self, *args, **kwargs):
        '''Turn the robot to the left.'''
        
        self.stopAnimate()
        self.robot.drive_wheel_motors(-self.speed, self.speed)
        return
    
    def moveLiftDown(self, *args, **kwargs):
        '''Move the lift down.'''
        
        self.stopAnimate()
        self.robot.move_lift(-self.liftSpeed)
        return
    
    def moveLiftUp(self, *args, **kwargs):
        '''Move the lift up.'''
        
        self.stopAnimate()
        self.robot.move_lift(self.liftSpeed)
        return
    
    def moveRight(self, *args, **kwargs):
        '''Turn the robot to the right.'''
       
        self.stopAnimate()
        self.robot.drive_wheel_motors(self.speed, -self.speed)
        return
    
    def stop(self, *args, **kwargs):
        '''Stop the robot.'''
        
        self.robot.stop_all_motors()
        return
    
    def stopHead(self, *args, **kwargs):
        '''Stop moving the head.'''

        self.robot.move_head(0)
        return
    
    def stopLift(self, *args, **kwargs):
        '''Stop moving the lift.'''

        self.robot.move_lift(0)
        return