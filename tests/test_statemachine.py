#!/usr/bin/env python

def ones_counter(val):
    print "ONES State: ",
    while 1:
        if val <= 0 or val >= 30:
            newState =  "OUT_OF_RANGE" ; break
        elif 20 <= val < 30:
            newState =  "TWENTIES"; break
        elif 10 <= val < 20:
            newState =  "TENS"; break
        else:
            print " @ %2.1f+" % val,
            val = math_func(val)
    print " >>"
    return (newState, val)

def tens_counter(val):
    print "TENS State: ",
    #raise ValueError,"I don't like %f"%val
    while 1:
        if val <= 0 or val >= 30:
            newState =  "OUT_OF_RANGE"; break
        elif 1 <= val < 10:
            newState =  "ONES"; break
        elif 20 <= val < 30:
            newState =  "TWENTIES"; break
        else:
            print " #%2.1f+" % val,
            val = math_func(val)
    print " >>"
    return (newState, val)

def twenties_counter(val):
    print "TWENTIES State:",
    while 1:
        if val <= 0  or  val >= 30:
            newState =  "OUT_OF_RANGE"; break
        elif 1 <= val < 10:
            newState =  "ONES"; break
        elif 10 <= val < 20:
            newState =  "TENS"; break
        else:
            print " *%2.1f+" % val,
            val = math_func(val)
    print " >>"
    return (newState, val)

def math_func(n):
    from math import sin
    return abs(sin(n))*31

def test_statemachine():
    from garpi.statemachine import StateMachine
    m = StateMachine("machine.state")
    m.add_state("ONES", ones_counter)
    m.add_state("TENS", tens_counter)
    m.add_state("TWENTIES", twenties_counter)
    m.add_state("OUT_OF_RANGE", None, end_state=1)

    m.run(1,"ONES")
    #m.run(1)

if __name__== "__main__":
    test_statemachine()
