'''

logger/spinner.py: Simple spinner for logger

Copyright (c) 2017-2018 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import sys

import sys
import time
import threading
from random import choice

class Spinner:
    spinning = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    @staticmethod
    def balloons_cursor():
        while 1: 
            for cursor in '. o O @ *': yield cursor

    @staticmethod
    def changing_arrows():
        while 1: 
            for cursor in '<^>v': yield cursor

    def select_generator(self, generator):
        if generator == None:
            generator = choice(['cursor',
                                'arrow',
                                'balloons'])

        return generator

    def __init__(self, delay=None, generator=None):
        generator = self.select_generator(generator)

        if generator == 'cursor':
            self.spinner_generator = self.spinning_cursor()
        elif generator == 'arrow':
            self.spinner_generator = self.changing_arrows()
        elif generator == 'balloons':
            self.spinner_generator = self.balloons_cursor()
            if delay is None: delay = 0.2
        else:
            self.spinner_generator = self.spinning_cursor()

        if delay and float(delay):
            self.delay = delay

    def run(self):
        while self.spinning:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.spinning = True
        threading.Thread(target=self.run).start()

    def stop(self):
        self.spinning = False
        time.sleep(self.delay)
