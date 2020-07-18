
# Retweet Graph Notes

Migrate and populate a few tables which we'll use to construct mention graphs.

First, for each tweet that is a retweet, determine the screen names of the user (i.e. retweeter) and the retweet user (i.e. retweeted) in a new table called "retweets":

```sql
DROP TABLE IF EXISTS impeachment_production.retweets;
CREATE TABLE IF NOT EXISTS impeachment_production.retweets as (
  SELECT
    user_id
    ,user_screen_name
    ,split(SPLIT(status_text, "@")[OFFSET(1)], ":")[OFFSET(0)] as retweet_user_screen_name
    ,status_id
    ,status_text
  FROM impeachment_production.tweets
  WHERE retweet_status_id is not null
);
```

> NOTE: this is an expensive query, as it is processing all 67M tweets. Bytes processed: 13.12 GB.

```sql
SELECT count(DISTINCT status_id)
FROM impeachment_production.retweets;
```

Of the 67M tweets, 55.9M are retweets.

Let's count how many times each user retweeted another, in a new table called "retweet_counts":

```sql
DROP TABLE IF EXISTS impeachment_production.retweet_counts;
CREATE TABLE IF NOT EXISTS impeachment_production.retweet_counts as (
  SELECT
    user_id
    ,user_screen_name
    ,retweet_user_screen_name
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.retweets
  GROUP BY 1,2,3
);
```

For the 55M retweets, there are 2.7M users who did the retweeting. This is compared to the 3.6M users total.

```sql
SELECT count(DISTINCT user_id)
FROM impeachment_production.retweet_counts;
```

It seems there are many users who retweeted themselves hundreds or thousands of times. Perhaps we want to filter them out of a table that will construct the rt graphs. Although it is possible they could indicate bot behavior.

```sql
SELECT user_id, user_screen_name, retweet_user_screen_name, retweet_count
FROM impeachment_production.retweet_counts
order by retweet_count desc
limit 100
```

Which users were retweeted the most?

```sql
select retweet_user_screen_name, count(distinct user_id) as rt_by_users_count, count(distinct status_id) as rt_count
from impeachment_production.retweets
group by 1
order by 2 desc
limit 25
```


retweet_user_screen_name | rt_by_users_count | rt_count
--- | --- | ---
realDonaldTrump | 330211 | 2572421
charliekirk11 | 261486 | 1235210
SethAbramson | 137606 | 536125
gtconway3d | 133292 | 536097
tribelaw | 121937 | 639320
RepAdamSchiff | 117465 | 293892
SpeakerPelosi | 114274 | 226393
funder | 112302 | 394151
dbongino | 110514 | 456759
DonaldJTrumpJr | 104977 | 334537
JoyceWhiteVance | 102185 | 472908
kylegriffin1 | 98250 | 389961
RepMarkMeadows | 98027 | 434223
RudyGiuliani | 89722 | 266291
marklevinshow | 87526 | 331255
GOPLeader | 87211 | 276222
mmpadellan | 80404 | 200454
RealJamesWoods | 79354 | 157840
joncoopertweets | 79340 | 212499
justinamash | 79183 | 166078
w_terrence | 78612 | 185069
TomFitton | 78148 | 405667
RyanAFournier | 78090 | 179753
TheRickWilson | 77116 | 172818
senatemajldr | 75212 | 191118


Identify which users were retweeted the most, about a given topic:

```sql
SELECT
  retweet_user_screen_name
  ,count(distinct user_id) as retweet_user_count
  ,sum(retweet_count) as retweeted_total
FROM (
  SELECT
    rt.user_id
    ,rt.user_screen_name
    ,rt.retweet_user_screen_name
    ,count(distinct status_id) as retweet_count
  FROM impeachment_production.retweets rt
  WHERE upper(rt.status_text) LIKE '%#IMPEACHANDCONVICT%' -- AND (created_at BETWEEN  AND '{end_at}')
    AND rt.user_screen_name <> rt.retweet_user_screen_name -- exlude people retweeting themselves, right?
  GROUP BY 1,2,3
  -- ORDER BY 4 desc
)
GROUP BY retweet_user_screen_name
ORDER BY 3 DESC
```

Constructing Retweet Graphs:

```json
{
  "app_env": "development",
  "job_id": "2020-06-15-2141",
  "dry_run": false,
  "batch_size": 1000,
  "dataset_address": "tweet-collector-py.impeachment_production",
  "destructive": false,
  "verbose": false,
  "retweeters": true,
  "conversation":

  {"users_limit": 50000, "topic": "impeach", "start_at": "2020-01-01", "end_at": "2020-01-30"}
}
```
