from unittest import TestSuite, TextTestRunner, TestLoader

import hashlib

def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)

def run_all(test_case_class):
    suite = TestLoader().loadTestsFromTestCase(test_case_class)
    TextTestRunner().run(suite)

def hash256(s):
    '''dwukrotne obliczenia skrótu sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()
