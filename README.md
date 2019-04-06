# etchasnap

**Etch-A-Snap** is (probably) the worlds first **Etch-A-Sketch Camera**. Powered by a Raspberry Pi Zero (or Zero W) it snaps photos just like any other camera, but outputs them by drawing to an *Pocket Etch-A-Sketch* screen. Quite slowly.

Photos are processed down to 100x60 pixel 1-bit (black & white) line drawings using `Pillow` and `OpenCV` and then translated into plotter commands using graph library `networkx`. The *Etch-A-Sketch* wheels are driven by two 5V stepper motors mounted into a custom 3D printed frame. The *Etch-A-Snap* is portable and powered by 4xAA batteries & 3x18650 LiPo cells.

The *developing time* for a photo is approximately 1 hour[^1]. 

![Etch-A-Snap front & back view](resources/etch-a-snap-front-and-back.jpg){: .center .small }

There is a full write-up with build instructions and code explanation [available here](https://www.twobitarcade.net/etch-a-snap).

The video below shows the entire process of taking a photo with the *Etch-A-Snap*, including the drawing of the image on the screen (as a timelapse) and the resulting picture.

,,,video


## Some other demos

,,,demo1
,,,demo2
,,,demo3


## Requirements

The following is required to run Etch-A-Snap. You don't need `gpiozero` when running the processing code in the Jupyter Notebook.

    opencv-python==4.0.0.21
    Pillow==6.0.0
    numpy==1.16.2
    gpiozero==1.4.0

## More stuff

The following bits and bobs are also available — 

* You can [download the STL](http://download.mfitzp.com/etch-a-snap-3d-prints.zip) files for 3D printing, or edit on [TinkerCad](https://www.tinkercad.com/things/13uotDFY1AL-etch-a-snap) with the model directly.
* The circuit [Fritzing file is also available](http://download.mfitzp.com/Etch-A-Snap.fzz).
