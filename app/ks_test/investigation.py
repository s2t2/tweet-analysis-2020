

import numpy as np
from scipy.stats import kstest, ks_2samp

np.random.seed(2020)

if __name__ == "__main__":

    # np.random.normal(center, spread, size)
    x = np.random.normal(0, 1, 10)
    y = np.random.normal(0, 1, 10)
    z = np.random.normal(1.1, 0.9, 10) # one of these things is not like the other
    print("X:", x) #> [-0.14235884,  2.05722174,  0.28326194,  1.32981198, -0.15462185, -0.06903086,  0.75518049,  0.82564665, -0.11306921, -2.36783759]
    print("Y:", y) #> [-0.16704943,  0.68539797,  0.02350011,  0.45620128,  0.27049278, -1.43500814,  0.88281715, -0.58008166, -0.5015653 ,  0.59095329]
    print("Z:", z) #> [0.44154537, 1.33557992, 0.32978398, 0.93122668, 0.76386234, 0.68422613, 0.36518051, 1.05938903, 1.209195  , 1.9333575 ]


    print("--------------------------")
    print("KS TESTS (AGAINST NORMAL DISTRIBUTION)...")
    print("X:", kstest(x, "norm")) #> KstestResult(statistic=0.33855972126320677, pvalue=0.1590112941560191)
    print("Y:", kstest(y, "norm")) #> KstestResult(statistic=0.18866753744918974, pvalue=0.8060547009565138)
    print("Z:", kstest(z, "norm")) #> KstestResult(statistic=0.6292184031091476, pvalue=0.0002318573221670418)

    print("--------------------------")
    print("TWO-SAMPLE KS TESTS...")
    print("X-Y:", ks_2samp(x, y)) #> KstestResult(statistic=0.3, pvalue=0.7869297884777761)
    print("X-Z:", ks_2samp(x, z)) #> KstestResult(statistic=0.6, pvalue=0.05244755244755244)
    print("Y-Z", ks_2samp(y, z)) #> KstestResult(statistic=0.6, pvalue=0.05244755244755244)


    #breakpoint()
