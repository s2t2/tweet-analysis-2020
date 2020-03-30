# Reproducibility Notes

## Notebook Conversion

Uploaded / imported the notebook [into colab](https://colab.research.google.com/drive/1T0ED71rbhiNF8HG-769aBqA0zZAJodcd), then select "File" > "Download .py" and store the result in the "start" dir.

## Database Queries

### Tweets

Counting users and tweets:

```sql
SELECT
  count(DISTINCT user_id) as user_count -- 3,600,545
  ,count(DISTINCT status_id) as tweet_count -- 67,655,058
FROM impeachment_production.tweets
```

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



## Database Migrations

Let's create a table of unique user ids and prepare to assemble network graphs:

```sql
CREATE TABLE IF NOT EXISTS impeachment_test.user_friends as (
  SELECT
    distinct(status_id) as user_id
    ,NULL as friend_ids
  FROM impeachment_test.tweets
  ORDER BY 1
);
```

## Resources

  + https://tweeterid.com/ for on-the-fly `user_id` / `screen_name` conversions
