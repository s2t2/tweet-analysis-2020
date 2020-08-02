# Dataset Exploration Notes

## Tweets

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

```sql
SELECT min(created_at) as first_at, max(created_at) as last_at FROM impeachment_production.tweets
```

first_at | last_at
--- | ---
2019-12-02 01:13:49 UTC | 2020-03-24 19:04:03 UTC


```sql
SELECT
  EXTRACT(YEAR from created_at) as year
  ,EXTRACT(MONTH from created_at) as month
  ,EXTRACT(WEEK from created_at) as week
  ,min(EXTRACT(DAY from created_at)) as first_day
  ,max(EXTRACT(DAY from created_at)) as last_day
  ,count(DISTINCT status_id) as tweet_count
  ,count(DISTINCT user_id) as user_count
FROM impeachment_production.tweets
GROUP BY 1,2,3
ORDER BY 1,2,3
```




```sql

SELECT
  CASE
    WHEN week = 0 THEN year - 1 -- treat first week of new year as the previous year
    ELSE year
    END  year

  ,CASE
    WHEN week = 0 THEN 52 -- treat first week of new year as the previous week
    ELSE week
    END  week

  ,count(DISTINCT day) as day_count
  ,min(created_at) as min_created
  ,max(created_at) as max_created
  ,count(DISTINCT status_id) as retweet_count
  ,count(DISTINCT user_id) as user_count
FROM (
  SELECT
    status_id
    ,user_id
    ,created_at
    ,EXTRACT(year from created_at) as year
    ,EXTRACT(month from created_at) as month
    ,EXTRACT(week from created_at) as week
    ,EXTRACT(day from created_at) as day
  FROM impeachment_production.retweets
  -- WHERE created_at BETWEEN "2019-12-15 00:00:00" AND "2020-03-21 23:59:59" -- get complete weeks
  limit 10000
) subq
GROUP BY 1,2
ORDER BY 1,2

```

year	| week	| day_count	| min_created	| max_created	| tweet_count	|user_count
---	| ---	| ---	| ---	| ---	| ---	|---
2019	| 48	| 1	| 2019-12-02 01:13:49 UTC	| 2019-12-02 03:23:14 UTC	| 2	        | 2
2019	| 49	| 3	| 2019-12-12 07:29:40 UTC	| 2019-12-14 23:59:59 UTC	| 4082497	  | 676812
2019	| 50	| 7	| 2019-12-15 00:00:00 UTC	| 2019-12-21 23:59:59 UTC	| 7419496	  | 1203537
2019	| 51	| 7	| 2019-12-22 00:00:00 UTC	| 2019-12-28 23:59:59 UTC	| 5303966	  | 880910
2019	| 52	| 7	| 2019-12-29 00:00:00 UTC	| 2020-01-04 23:59:59 UTC	| 3564155	  | 778148
2020	| 1	  | 7	| 2020-01-05 00:00:00 UTC	| 2020-01-11 23:59:59 UTC	| 4729694	  | 780629
2020	| 2	  | 7	| 2020-01-12 00:00:00 UTC	| 2020-01-18 23:59:59 UTC	| 7344094	  | 914259
2020	| 3	  | 7	| 2020-01-19 00:00:00 UTC	| 2020-01-25 23:59:59 UTC	| 9090452	  | 955223
2020	| 4	  | 7	| 2020-01-26 00:00:00 UTC	| 2020-02-01 23:59:59 UTC	| 9614217	  | 1064299
2020	| 5	  | 7	| 2020-02-02 00:00:00 UTC	| 2020-02-08 23:59:59 UTC	| 7269314	  | 1016836
2020	| 6	  | 7	| 2020-02-09 00:00:00 UTC	| 2020-02-15 23:59:59 UTC	| 3170176	  | 589573
2020	| 7	  | 7	| 2020-02-16 00:00:00 UTC	| 2020-02-22 23:59:59 UTC	| 1538486	  | 415831
2020	| 8	  | 7	| 2020-02-23 00:00:00 UTC	| 2020-02-29 23:59:59 UTC	| 824646	  | 283137
2020	| 9	  | 7	| 2020-03-01 00:00:00 UTC	| 2020-03-07 23:59:59 UTC	| 930076	  | 323864
2020	| 10	| 7	| 2020-03-08 00:00:00 UTC	| 2020-03-14 23:59:59 UTC	| 1183346	  | 381776
2020	| 11	| 7	| 2020-03-15 00:00:01 UTC	| 2020-03-21 23:59:59 UTC	| 946883	  | 387214
2020	| 12	| 3	| 2020-03-22 00:00:00 UTC	| 2020-03-24 19:04:03 UTC	| 655057	  | 261301




## Topics

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

Counting tweets by topic (not mutually exclusive):


```sql
select

count(distinct t.user_id) as user_count
,count(distinct t.status_id) as status_count

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Trump to Pelosi')) then status_id end) as topic_to_pelosi
--,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachAndConvictTrump')) then status_id end) as ____________
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#IGHearing')) then status_id end) as topic_ig_hearing
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('impeach')) then status_id end) as topic_impeach
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachAndConvict')) then status_id end) as topic_impeach_convict
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#TrumpImpeachment')) then status_id end) as topic_trump_impeachment
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#IGReport')) then status_id end) as topic_ig_report
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('impeached')) then status_id end) as topic_impeached
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#SenateHearing')) then status_id end) as topic_senate_hearing
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('impeachment')) then status_id end) as topic_impeachment
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#FactsMatter')) then status_id end) as topic_facts
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachmentRally')) then status_id end) as topic_rally
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachmentEve')) then status_id end) as topic_eve
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachAndRemove')) then status_id end) as topic_impeach_remove
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#trumpletter')) then status_id end) as topic_letter
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#NotAboveTheLaw')) then status_id end) as topic_not_above
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#25thAmendmentNow')) then status_id end) as topic_25th
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ShamTrial')) then status_id end) as topic_sham_trial
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#GOPCoverup')) then status_id end) as topic_gop_coverup
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#MitchMcCoverup')) then status_id end) as topic_mitch_mccoverup
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#AquittedForever')) then status_id end) as topic_acq_forever
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#CoverUpGOP')) then status_id end) as topic_coverup_gop
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#MoscowMitch')) then status_id end) as topic_moscow_mitch
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#CountryOverParty')) then status_id end) as topic_country_over_party

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('sham')) then status_id end) as topic_sham
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('hoax')) then status_id end) as topic_hoax
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('witch')) then status_id end) as topic_witch
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('hunt')) then status_id end) as topic_hunt

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Trump')) then status_id end) as topic_trump
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Pelosi')) then status_id end) as topic_pelosi
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Schumer')) then status_id end) as topic_schumer
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Schiff')) then status_id end) as topic_schiff
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Nadler')) then status_id end) as topic_nadler
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Yovanovitch')) then status_id end) as topic_yov
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Vindman')) then status_id end) as topic_vind
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Volker')) then status_id end) as topic_volk
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Sondland')) then status_id end) as topic_sond
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('AMIGOS')) then status_id end) as topic_amigos
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Fiona Hill')) then status_id end) as topic_fiona
--,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('George Kent')) then status_id end) as ________________
-- ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('William Taylor')) then status_id end) as ________________
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Bolton')) then status_id end) as topic_bolton
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Zelensk')) then status_id end) as topic_z

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@realDonaldTrump')) then status_id end) as mention_trump
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@senatemajldr')) then status_id end) as mention_mitch
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@SpeakerPelosi')) then status_id end) as mention_pelosi
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@SenSchumer')) then status_id end) as mention_schumer
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@JoeBiden')) then status_id end) as mention_biden
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@GOP')) then status_id end) as mention_gop
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@Dems')) then status_id end) as mention_dems

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@nytimes')) then status_id end) as mention_nytimes
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@WSJ')) then status_id end) as mention_wsj
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@CNN')) then status_id end) as mention_cnn
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@MSNBC')) then status_id end) as mention_msnbc
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@NBCNews')) then status_id end) as mention_nbcnews
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@abcnews')) then status_id end) as mention_abcnews
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@thehill')) then status_id end) as mention_thehill
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@politico')) then status_id end) as mention_politico

from impeachment_production.tweets t
```

Refining...

```sql
select

count(distinct t.user_id) as user_count
,count(distinct t.status_id) as status_count

-- TAGS

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#MAGA')) then status_id end) as tag_maga
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#MoscowMitch')) then status_id end) as tag_moscow_mitch
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#FactsMatter')) then status_id end) as tag_facts_matter
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#TrumpImpeachment')) then status_id end) as tag_trump_impeachment

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#MitchMcCoverup'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('#CoverUpGOP'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('#GOPCoverup')) then status_id end) as tag_coverup

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachAndConvict'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachAndRemove')) then status_id end) as tag_convict_remove


,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#IGHearing'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('#IGReport')) then status_id end) as tag_ig

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachmentRally'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('#ImpeachmentEve')) then status_id end) as tag_eve

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#NotAboveTheLaw')) then status_id end) as tag_not_above
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#25thAmendmentNow')) then status_id end) as tag_25th
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#CountryOverParty')) then status_id end) as tag_country_over_party

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#ShamTrial')) then status_id end) as tag_sham_trial
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('#AquittedForever')) then status_id end) as tag_acq_forever

-- TERMS

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('impeach')) then status_id end) as topic_impeach
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('sham')) then status_id end) as topic_sham
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('hoax')) then status_id end) as topic_hoax
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('witch'))
                       AND REGEXP_CONTAINS(upper(t.status_text), upper('hunt')) then status_id end) as topic_witch_hunt
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('coverup'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('cover-up'))
                       OR REGEXP_CONTAINS(upper(t.status_text), upper('cover up')) then status_id end) as topic_coverup

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Pelosi')) then status_id end) as topic_pelosi
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Trump')) then status_id end) as topic_trump
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Schiff')) then status_id end) as topic_schiff
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Nadler')) then status_id end) as topic_nadler
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Yovanovitch')) then status_id end) as topic_yov
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Vindman')) then status_id end) as topic_vindman
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Volker')) then status_id end) as topic_volker
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Sondland')) then status_id end) as topic_sondland
--,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('AMIGOS')) then status_id end) as topic_amigos
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Fiona Hill')) then status_id end) as topic_fiona
--,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('George Kent')) then status_id end) as ________________
-- ,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('William Taylor')) then status_id end) as ________________
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Bolton')) then status_id end) as topic_bolton
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('Zelensk')) then status_id end) as topic_z
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('hunter')) then status_id end) as topic_hunter
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('biden')) then status_id end) as topic_biden

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@realDonaldTrump')) then status_id end) as mention_trump
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@senatemajldr')) then status_id end) as mention_mitch
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@SpeakerPelosi')) then status_id end) as mention_pelosi
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@SenSchumer')) then status_id end) as mention_schumer
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@JoeBiden')) then status_id end) as mention_biden
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@GOP')) then status_id end) as mention_gop
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@TheDemocrats')) then status_id end) as mention_dems

,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@nytimes')) then status_id end) as mention_nytimes
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@WSJ')) then status_id end) as mention_wsj
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@CNN')) then status_id end) as mention_cnn
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@MSNBC')) then status_id end) as mention_msnbc
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@NBCNews')) then status_id end) as mention_nbcnews
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@abcnews')) then status_id end) as mention_abcnews
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@thehill')) then status_id end) as mention_thehill
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@politico')) then status_id end) as mention_politico
,count(distinct case when REGEXP_CONTAINS(upper(t.status_text), upper('@ap ')) then status_id end) as mention_ap
from impeachment_production.tweets t
```
