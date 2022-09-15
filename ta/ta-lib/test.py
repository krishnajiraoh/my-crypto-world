import talib
import numpy as np

def test():
    c = np.random.randn(40)
    print(talib.SMA(c))

if __name__ == '__main__':
    test()