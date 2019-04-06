import time

from gpiozero import Button, LED, PWMLED

import graph, plotter, camera


red = LED(21)
yellow = PWMLED(20)
green = LED(16)

shutter = Button(25)


# Status light shortcuts.
def status_ready():
    green.on()
    yellow.off()
    red.off()

def status_processing():
    green.off()
    red.off()
    yellow.on()
    


def main():
    while True:
                
        # Setup the camera interface.
        camera.prepare()
        status_ready()
        
        # Wait for shutter, then take picture.
        shutter.wait_for_press()
        status_processing()
        image = camera.take_photo()

    
if __name__ == "__main__":
    main()