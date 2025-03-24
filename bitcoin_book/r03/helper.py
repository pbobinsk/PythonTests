from unittest import TestSuite, TextTestRunner

import hashlib


def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)


def hash256(s):
    '''dwukrotne obliczenia skrótu sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()
