import time
import cozmo
import cozmo.world as cworld
from cozmo.util import degrees, distance_mm, speed_mmps
from cozmo.exceptions import RobotBusy

def newImage(*args, **kwargs):
   print('test')
   image = kwargs['image'].raw_image
   print(image)
   return

def test(robot):

   robot.camera.image_stream_enabled = True
   robot.add_event_handler(cozmo.world.EvtNewCameraImage, newImage)

   while True:
      try:
#         robot.drive_straight(distance_mm(100), speed_mmps(10), should_play_anim=True)
         time.sleep(3)
      except RobotBusy:
         pass
   return

cozmo.run_program(test) #, use_viewer=True)
