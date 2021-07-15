# Notes

## Toxicity Models

Using the Detoxify package for toxicity classification transformer models. For a list of available models and their descriptions, see the [Detoxify Docs](https://github.com/unitaryai/detoxify#prediction).

  + `original`: `bert-base-uncased` / Toxic Comment Classification Challenge
  + `unbiased`: `roberta-base` / Unintended Bias in Toxicity Classification

## Comparing Models

There are some differences between the two main toxicity models. We'll probably want the results of both unless we have a preference for methodological reasons.

```sh
(tweet-analyzer-env-38)  --->> python -m app.toxicity.investigate_models

#> ----------------
#>
#> TEXT: 'RT @realDonaldTrump: I was very surprised &amp; disappointed that Senator Joe Manchin of West Virginia voted against me on the Democrat’s total…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.000993     1.004200e-04  0.000182  0.000117  0.000180       0.000141  original
#> 1  0.000588     9.500000e-07  0.000040  0.000026  0.000216            NaN  unbiased
#>
#> ----------------
#>
#> TEXT: 'RT @realDonaldTrump: Crazy Nancy Pelosi should spend more time in her decaying city and less time on the Impeachment Hoax! https://t.co/eno…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.126401         0.000225  0.001830  0.000507  0.009287       0.001832  original
#> 1  0.367150         0.000003  0.000419  0.000169  0.296279            NaN  unbiased
#> ----------------
#>
#> TEXT: 'RT @SpeakerPelosi: The House cannot choose our impeachment managers until we know what sort of trial the Senate will conduct. President Tr…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.000855     1.146300e-04  0.000166  0.000138  0.000186       0.000157  original
#> 1  0.000636     8.700000e-07  0.000041  0.000025  0.000246            NaN  unbiased
#>
#> ----------------
#>
#> TEXT: 'RT @RepAdamSchiff: Lt. Col. Vindman did his job. As a soldier in Iraq, he received a Purple Heart. Then he displayed another rare form o…'
#>
#> SCORES:
#>    toxicity  severe_toxicity   obscene    threat    insult  identity_hate     model
#> 0  0.001845         0.000100  0.000289  0.000095  0.000234       0.000162  original
#> 1  0.000909         0.000002  0.000063  0.000141  0.000227            NaN  unbiased
```

Looks like the unbiased model has different class names actually:

```sh
'toxicity',
'severe_toxicity',
'obscene',
'identity_attack',
'insult',
'threat',
'sexual_explicit'
```

> UPDATE: we're just going with the original BERT model for now.


## Benchmarking Batch Sizes

The models are capable of scoring many texts at a time. But how many is most efficient?

```sh
python -m app.toxicity.investigate_benchmarks

#> ---------------------
#> MODEL: ORIGINAL
#> ['toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
#> ---------------------
#> PROCESSED 1 ITEMS IN 0.06 SECONDS (16.67 items / second)
#> ---------------------
#> PROCESSED 10 ITEMS IN 0.21 SECONDS (47.62 items / second)
#> ---------------------
#> PROCESSED 100 ITEMS IN 1.81 SECONDS (55.25 items / second)
#> ---------------------
#> PROCESSED 1000 ITEMS IN 17.49 SECONDS (57.18 items / second)
#> ---------------------
#> PROCESSED 10000 ITEMS IN 192.87 SECONDS (51.85 items / second)
#> ---------------------
```

The highest processing rate for the toxicity model seems to be around 1,000 texts at a time (50 per second, 300 per minute, 180K per hour, 4.32M per day). This can work. We'd need to run server for like 3 days. Very reasonable.

> UPDATE: the server may only have enough memory to process batches of 20.
