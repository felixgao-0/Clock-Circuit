# Used to time the code and figure out why my stuff is SO SLOW
import time

def timeit(f, *args, **kwargs):
    myname = f.__name__
    def new_func(*args, **kwargs):
        t = time.ticks_us()
        result = f(*args, **kwargs)
        delta = time.ticks_diff(time.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func
