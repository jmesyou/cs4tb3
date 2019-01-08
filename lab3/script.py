#!/bin/python3

'''
names: James You, Zichen Jiang
'''
import sys

stream = None

B = ['t', 'f']
D = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
L = ['a', 'b', 'c', 'd', 'e']

def peek():
    global stream
    return stream[0]

def accept(char):
    global stream
    if len(stream) == 0:
        raise IndexError
    sym = peek()
    if sym == char or sym in char:
        stream.pop(0)
    else:
        raise SyntaxError

def main():
    global stream
    stream = list(sys.stdin.readline())
    try:
        Q()
        accept("\n")
        assert(len(stream) == 0)
        sys.stdout.write("accepted\n")
    except:
        sys.stdout.write("rejected\n")


def Q():
    accept('w')
    accept('(')
    E()
    accept(')')
    accept('{')
    while True:
        try:
            accept('}')
            break
        except SyntaxError:
            S()
    return

def S():
    V()
    accept('=')
    E()
    accept(';')
    return

def V():
    I()
    sym = peek()
    if sym == '[':
        accept('[')
        E()
        accept(']')
    else:
        return

def I():
    accept(L)
    try:
        while True:
            accept(L)
    except SyntaxError:
        return

def N():
    accept(D)
    try:
        while True:
            accept(D)
    except SyntaxError:
        return

def E():

    sym = peek()
    if sym == '(':
        accept('(')
        E()
        accept(')')
    elif sym in B:
        accept(B)
        accept(['|', "&"])
        accept(B)
    elif sym in D:
        N()
        accept(['+', '-'])
        N()
    else:
        raise SyntaxError

main()
