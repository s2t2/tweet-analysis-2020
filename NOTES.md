# Reproducibility Notes

## Notebook Conversion

Uploaded / imported [this notebook](/start/follower_network_collector.ipynb) [into colab](https://colab.research.google.com/drive/1T0ED71rbhiNF8HG-769aBqA0zZAJodcd), then selected "File" > "Download .py" and stored the [resulting python script](/start/follower_network_collector.py) in the "start" dir.

## Database Resources

Working with BigQuery:

  + https://cloud.google.com/bigquery/docs/reference/standard-sql/operators
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/conversion_rules

## Database Queries

### Tweets

Counting users and tweets:

```sql
SELECT
  count(DISTINCT user_id) as user_count -- 3,600,545
  ,count(DISTINCT status_id) as tweet_count -- 67,655,058
FROM impeachment_production.tweets
```

tweet_count	| user_count
---	        | ---
67,655,058	| 3,600,545

Counting users and tweets per month:

```sql
SELECT
  EXTRACT(YEAR from created_at) as year
  ,EXTRACT(MONTH from created_at) as month
  ,min(EXTRACT(DAY from created_at)) as first_day
  ,max(EXTRACT(DAY from created_at)) as last_day
  ,count(DISTINCT status_id) as tweet_count
  ,count(DISTINCT user_id) as user_count
FROM impeachment_production.tweets
GROUP BY 1,2
ORDER BY 1,2
```

year	| month	| first_day	| last_day  | tweet_count	| user_count
---	    | ---	| ---	    | ---       | ---	        | ---
2019	| 12	| 2	        | 31        | 18,239,072	| 1,860,878
2020	| 1	    | 1	        | 31        | 31,504,261	| 2,105,059
2020	| 2	    | 1	        | 29        | 14,207,862	| 1,416,178
2020	| 3	    | 1	        | 24        | 3,715,362	    | 789,737

Over 67.6M tweets from over 3.6M users were collected during the period from December 2, 2019 through March 24, 2020.

### Topics

Listing topics (25):

```sql
SELECT *
FROM impeachment_production.topics
```

topic	                | created_at
---	                    | ---
Trump to Pelosi	        | 2019-12-17 17:48:23 UTC
#ImpeachAndConvictTrump	| 2019-12-17 17:48:23 UTC
#IGHearing	            | 2019-12-17 17:48:23 UTC
impeach	                | 2019-12-17 17:48:23 UTC
#ImpeachAndConvict	    | 2019-12-17 17:48:23 UTC
#TrumpImpeachment	    | 2019-12-17 17:48:23 UTC
#IGReport	            | 2019-12-17 17:48:23 UTC
impeached	            | 2019-12-17 17:48:23 UTC
#SenateHearing	        | 2019-12-17 17:48:23 UTC
impeachment	            | 2019-12-17 17:48:23 UTC
#FactsMatter	        | 2019-12-17 17:48:23 UTC
#ImpeachmentRally	    | 2019-12-18 06:37:35 UTC
#ImpeachmentEve	        | 2019-12-18 06:18:08 UTC
#ImpeachAndRemove	    | 2019-12-18 06:35:29 UTC
#trumpletter	        | 2019-12-18 06:29:40 UTC
#NotAboveTheLaw	        | 2019-12-18 07:42:53 UTC
#25thAmendmentNow	    | 2019-12-18 07:42:16 UTC
#ShamTrial	            | 2020-01-22 03:59:06 UTC
#GOPCoverup	            | 2020-01-22 03:59:24 UTC
#MitchMcCoverup	        | 2020-02-06 01:37:48 UTC
#AquittedForever	    | 2020-02-06 01:37:05 UTC
#CoverUpGOP	            | 2020-02-06 01:36:36 UTC
#MoscowMitch	        | 2020-02-06 01:37:30 UTC
#CountryOverParty	    | 2020-02-06 01:37:13 UTC





## Twitter Resources

Ad-hoc conversions between user ids and screen names:
  + https://tweeterid.com/

Working with the `twint` package:
  + https://github.com/twintproject/twint
  + https://pielco11.ovh/posts/twint-osint/#followersfollowing
  + https://github.com/twintproject/twint/pull/685
  + https://github.com/twintproject/twint/wiki/Storing-objects-in-RAM
  + https://github.com/twintproject/twint/issues/270
  + https://github.com/twintproject/twint/issues/704

## Partitioning Users

Will be running friend collection in a distributed way, so fetching buckets of users to assign to each server at one time or another.

```sql
SELECT
  partition_id
  ,count(DISTINCT user_id) as user_count
  ,min(user_id) as min_id
  ,max(user_id) as max_id
FROM (
  SELECT
    NTILE(10) OVER (ORDER BY CAST(user_id as int64)) as partition_id
    ,CAST(user_id as int64) as user_id
  FROM (SELECT DISTINCT user_id FROM impeachment_production.tweets)
) user_partitions
GROUP BY partition_id
```

partition_id    | user_count	| min_id	            | max_id
---	            | ---	        | ---	                | ---
1	            | 360055	    | 17	                | 49223966
2	            | 360055	    | 49224083	            | 218645473
3	            | 360055	    | 218645600	            | 446518003
4	            | 360055	    | 446520525	            | 1126843322
5	            | 360055	    | 1126843458	        | 2557922900
6	            | 360054	    | 2557923828	        | 4277913148
7	            | 360054	    | 4277927001	        | 833566039577239552
8	            | 360054	    | 833567097506533376	| 1012042187482202113
9	            | 360054	    | 1012042227844075522	| 1154556355883089920
10	            | 360054	    | 1154556513031266304	| 1242523027058769920
