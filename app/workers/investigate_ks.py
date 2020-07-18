

import numpy as np
from scipy.stats import kstest, ks_2samp

np.random.seed(99)

if __name__ == "__main__":

    x = np.random.normal(0, 1, 10)
    y = np.random.normal(0, 1, 10)
    z = np.random.normal(1.1, 0.9, 10) # one of these things is not like the other

    print("--------------------------")
    print("AVERAGES...")
    print("X:", np.mean(x)) #> X: 0.24042044332257215
    print("Y:", np.mean(y)) #> Y: 0.022565803383464623
    print("Z:", np.mean(z)) #> Z: 0.9053346451353391

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
