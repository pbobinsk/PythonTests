import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bitcoin_module.helper import run, run_all
import bitcoin_module.ecc as ecc
from bitcoin_module.ecc import FieldElement

if __name__ == "__main__":
    a = FieldElement(7, 13)
    b = FieldElement(6, 13)
    print(a == b)
    print(a == a)

    run(ecc.FieldElementTest("test_ne"))

    run_all(ecc.FieldElementTest)