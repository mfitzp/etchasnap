import threading
import queue
import time

from motor import left, right, up, down, stop, stop_lr, stop_ud


MOVE_MAP = {
    # Directions.
    'left': left, 
    'right': right, 
    'up': up, 
    'down': down, 
    # Stop actions.
    'stop': stop,       # Stop held.
    'stop_lr': stop_lr, # Stop lr loose.
    'stop_ud': stop_ud, # Stop ud loose.
}

# Screen resolution @ scale 50 = 125w 75h


MIN_STEP_WAIT = 0.001
PLOTTER_SCALE = 25
REVERSE_TRACKING_STEPS = 100 // PLOTTER_SCALE  # Tracking steps = 100

# The queue that holds our list of moves in terms of MOVE_MAP (individual steps).
movequeue = queue.Queue()


def hhmmss(s):
    # s = 1
    # m = 60
    # h = 360
    h, r = divmod(s, 360)
    m, r = divmod(r, 60)
    s, _ = divmod(r, 1)
    return ("%d:%02d:%02d" % (h,m,s)) if h else ("%d:%02d" % (m,s))


def plot():
    """
    Pull an individual move off the queue and perform it, at most 
    every MIN_STEP_WAIT seconds.
    """    
    move_n = 0
    
    while True:
        
        # Retrieve a move tuple from the queue, and execute.
        action, lr, ud = movequeue.get()
        move_n += 1

        for n in range(PLOTTER_SCALE):
            # Check time
            now = time.time()
            
            MOVE_MAP[lr]()
            MOVE_MAP[ud]()

            # Wait if the get wasn't already too long.
            while time.time() < now + MIN_STEP_WAIT:
                time.sleep(0.001)

            seconds_remaining = movequeue.qsize() * MIN_STEP_WAIT * PLOTTER_SCALE
            print("{:>8} {:>7},{:>7},{:>7} {:>2}: eta {}    ".format(
                move_n,
                action,
                lr,
                ud, 
                n,
                hhmmss(seconds_remaining)
            ), end='\r')


def sign(n):
    """
    Return -1 for negative numbers, +1 for positive or 0 for zero.
    """
    if n == 0: return 0
    return n / abs(n)
        

def enqueue(moves):
    """
    Iterate a generator of moves, converting macro moves (+4, +4) to a series of individual
    steps and pushing these onto the plotter queue (+1, +1) x 4.
    """
    # Returning to home will always put the wheels in this state.
    lr, prev_lr = 'left', 'left'
    ud, prev_ud = 'up', 'up'
    
    for diff_x, diff_y in moves:
        
        # Select the lr/ud based on magnitude. For 0, keep current so we 
        # can easily detect changes in direction across stoppages for tracking.
        lr = {-1: 'left', +1: 'right', 0: lr}[sign(diff_x)]
        ud = {-1: 'up', +1: 'down', 0: ud}[sign(diff_y)]

        # Apply tracking correction for changes in direction.
        if (lr != prev_lr) or (ud != prev_ud):
            tracking = (
                'track',
                lr if (lr != prev_lr) else 'stop',
                ud if (ud != prev_ud) else 'stop',
            )            
            for n in range(REVERSE_TRACKING_STEPS):
                movequeue.put(tracking)

        # Perform move.

        a_diff_x = abs(diff_x)
        a_diff_y = abs(diff_y)

        if a_diff_x and a_diff_y:
            # We can cheat at abit, as we only have 45' angles, i.e. a_diff_x == a_diff_y.
            for _ in range(a_diff_x):
                movequeue.put(('move', lr, ud))
            
        elif not a_diff_y:
            for _ in range(a_diff_x):
                movequeue.put(('move', lr, 'stop'))

        elif not a_diff_x:
            for _ in range(a_diff_y):
                movequeue.put(('move', 'stop', ud))
    
        prev_lr, prev_ud = lr, ud
    

    # Send stop all directions (unheld).
    movequeue.put(('home', 'stop_lr', 'stop_ud'))
    
    # Wait for the queue to empty.
    while movequeue.qsize():
        time.sleep(1)


thread = threading.Thread(target=plot, daemon=True)
thread.start()

