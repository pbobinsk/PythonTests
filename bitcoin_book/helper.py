from unittest import TestSuite, TextTestRunner, TestLoader


def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)

def run_all(test_case_class):
    suite = TestLoader().loadTestsFromTestCase(test_case_class)
    TextTestRunner().run(suite)
