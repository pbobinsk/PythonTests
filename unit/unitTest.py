import unittest
import unitMain as mut

class TestClass(unittest.TestCase):
    def test_add(self):
        self.assertEqual(5,mut.add(2,3))


    def test_sub(self):
        self.assertEqual(-1,mut.sub(2,3))

    def test_mul(self):
        self.assertEqual(8,mut.mul(2,4))

    def test_div(self):
        self.assertEqual(4,mut.div(12,3))
        self.assertRaises(ZeroDivisionError,mut.div, 10, 0)


if __name__=='__main__':
    unittest.main()
    