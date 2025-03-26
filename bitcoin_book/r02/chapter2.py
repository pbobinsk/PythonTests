import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import run, run_all
import bitcoin_module.ecc as ecc
from bitcoin_module.ecc import Point

if __name__ == "__main__":
    p1 = Point(-1, -1, 5, 7)
    # p2 = Point(-1, -2, 5, 7)

    run(ecc.PointTest("test_ne"))

    run_all(ecc.PointTest)