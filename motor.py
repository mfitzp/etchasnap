from gpiozero import OutputDevice, LED


lr1 = OutputDevice(26)
lr2 = OutputDevice(19)
lr3 = OutputDevice(13)
lr4 = OutputDevice(6)

lr_steps = [
    (lr1.on,  lr2.on,  lr3.off, lr4.off),
    (lr1.off, lr2.on,  lr3.on,  lr4.off),
    (lr1.off, lr2.off, lr3.on,  lr4.on),
    (lr1.on,  lr2.off, lr3.off, lr4.on),
]

ud1 = OutputDevice(10)
ud2 = OutputDevice(22)
ud3 = OutputDevice(27)
ud4 = OutputDevice(17)

ud_steps = [
    (ud1.on,  ud2.on,  ud3.off, ud4.off),
    (ud1.off, ud2.on,  ud3.on,  ud4.off),
    (ud1.off, ud2.off, ud3.on,  ud4.on),
    (ud1.on,  ud2.off, ud3.off, ud4.on),
]

# Step iteration counters.
lr = 1
ud = 1



def step(steps, i):
    for p in steps[i]:
        p()


def right():
    global lr
    lr -= 1
    if lr == -1:
        lr = 3
    step(lr_steps, lr)

        
def left():
    global lr
    lr += 1
    if lr == 4:
        lr = 0
    step(lr_steps, lr)


def up():
    global ud
    ud -= 1
    if ud == -1:
        ud = 3
    step(ud_steps, ud)

        
def down():
    global ud
    ud += 1
    if ud == 4:
        ud = 0
    step(ud_steps, ud)


def stop():
    pass


def stop_lr():
    for p in [lr1, lr2, lr3, lr4]:
        p.off()


def stop_ud():
    for p in [ud1, ud2, ud3, ud4]:
        p.off()

