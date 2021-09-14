# News Source Scoring

Using a third-party [ranking of news sources](https://www.pnas.org/content/pnas/suppl/2019/01/14/1806781116.DCSupplemental/pnas.1806781116.sapp.pdf) from [Fighting misinformation on social media using crowdsourced judgments of news source quality](https://www.pnas.org/content/116/7/2521#sec-3) by Pennycook and Rand.

Thanks to Qi Yang for sharing this paper and providing the corresponding [CSV file of rankings](data/news_outlet_rankings.csv).

## Queries

We can load the CSV file into a table, then use queries to perform the analysis.

```sql
--SELECT expanded_url, count(distinct status_id) as status_count
--FROM `tweet-collector-py.impeachment_production.recollected_status_urls`
--WHERE NOT REGEXP_CONTAINS(expanded_url, 'https://twitter.com/')
--GROUP BY 1
--ORDER BY 2 DESC
--LIMIT 25
```

Top domains:

```sql
#standardSQL

WITH domains as (
    SELECT
        regexp_replace(
            split(split(expanded_url, "://")[OFFSET(1)], "/")[OFFSET(0)]
            , "www.", ""
        ) url_domain
        --split(split(expanded_url, "://")[OFFSET(1)], "/")[OFFSET(0)] url_www_domain
        --,split(expanded_url, "://")[OFFSET(1)] as url_stem
        ,expanded_url
        ,status_id
   FROM `tweet-collector-py.impeachment_production.recollected_status_urls`
   --LIMIT 10
)

SELECT url_domain, count(distinct status_id) as status_count
FROM domains
GROUP BY 1
ORDER BY 2 DESC
LIMIT 250
```

## Migrations

Extracting domains from the URLS:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.recollected_status_url_domains`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_status_url_domains`  as (
    SELECT
         status_id
         ,expanded_url
        , regexp_replace(
            split(split(expanded_url, "://")[OFFSET(1)], "/")[OFFSET(0)]
            , "www.", ""
        ) url_domain
   FROM `tweet-collector-py.impeachment_production.recollected_status_urls`
   --LIMIT 10
)
```

```sql
SELECT url_domain, count(distinct status_id) as status_count
FROM `tweet-collector-py.impeachment_production.recollected_status_url_domains`
GROUP BY 1
ORDER BY 2 DESC
LIMIT 250
```


Uploading a table of fact check scores from [CSV file](data/domain_fact_scores.csv) to `domain_fact_scores` table... Make sure to check "auto-generate schema".

```sql
SELECT domain, fact_score, fact_category
FROM `tweet-collector-py.impeachment_production.domain_fact_scores`
ORDER BY fact_score DESC
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.recollected_status_fact_scores`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_status_fact_scores` as (
   SELECT
      urls.status_id
      ,urls.expanded_url
      ,urls.url_domain
      ,facts.domain as fact_domain
      ,facts.fact_score
      ,facts.fact_category
   FROM `tweet-collector-py.impeachment_production.recollected_status_url_domains` urls
   LEFT JOIN `tweet-collector-py.impeachment_production.domain_fact_scores` facts ON facts.domain = urls.url_domain
   WHERE facts.id IS NOT NULL
   --ORDER BY fact_score DESC
   --LIMIT 10
)
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.recollected_user_fact_scores`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_user_fact_scores` as (
    SELECT
        t.user_id
        ,count(distinct f.status_id) as status_count
        ,avg(f.fact_score) as avg_fact_score
    FROM `tweet-collector-py.impeachment_production.recollected_status_fact_scores` f
    JOIN `tweet-collector-py.impeachment_production.recollected_statuses` t on t.status_id = f.status_id
    --LEFT JOIN `tweet-collector-py.impeachment_production.user_details_v6_slim` u on u.user_id = t.user_id
    GROUP BY 1
    --ORDER BY 2 DESC
    --LIMIT 50
);
```

## Preliminary Analysis

```sql
SELECT count(distinct status_id)
FROM `tweet-collector-py.impeachment_production.recollected_status_urls`
-- 7,405,940
```

```sql
SELECT
   count(distinct status_id) as status_count
   ,avg(fact_score) as avg_fact_score
   ,min(fact_score) as min_fact_score
   ,max(fact_score) as max_fact_score
FROM `tweet-collector-py.impeachment_production.recollected_status_fact_scores`
```


status_count	| avg_fact_score	| min_fact_score	| max_fact_score
--- | --- | --- | ---
912,633	| 3.10	| 1.00	| 4.71

What about aggregates for each user group?

```sql
SELECT
   count(distinct uf.user_id) as user_count

   ,avg(uf.status_count) as avg_status_count

   ,avg(uf.avg_fact_score) as avg_fact_all
    ,avg(CASE WHEN u.is_bot=true            THEN uf.avg_fact_score END) as fact_bot
    ,avg(CASE WHEN u.is_bot=false           THEN uf.avg_fact_score END) as fact_human
    ,avg(CASE WHEN u.is_q=true              THEN uf.avg_fact_score END) as fact_q
    ,avg(CASE WHEN u.is_q=false             THEN uf.avg_fact_score END) as fact_nonq
    ,avg(CASE WHEN u.bot_rt_network=0       THEN uf.avg_fact_score END) as fact_bot0
    ,avg(CASE WHEN u.bot_rt_network=1       THEN uf.avg_fact_score END) as fact_bot1
    ,avg(CASE WHEN u.opinion_community=0    THEN uf.avg_fact_score END) as fact_op0
    ,avg(CASE WHEN u.opinion_community=1    THEN uf.avg_fact_score END) as fact_op1

FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u
JOIN `tweet-collector-py.impeachment_production.recollected_user_fact_scores` uf ON u.user_id = uf.user_id
```


```sql
SELECT
   count(distinct uf.user_id) as user_count
   ,sum(uf.status_count) as total_status_count
   ,avg(uf.status_count) as avg_status_count
   ,avg(uf.avg_fact_score) as avg_fact_score



    ,sum(CASE WHEN u.is_bot=true            THEN uf.status_count END) as count_bot
    ,sum(CASE WHEN u.is_bot=false           THEN uf.status_count END) as count_human
    ,sum(CASE WHEN u.is_q=true              THEN uf.status_count END) as count_q
    ,sum(CASE WHEN u.is_q=false             THEN uf.status_count END) as count_nonq
    ,sum(CASE WHEN u.bot_rt_network=0       THEN uf.status_count END) as count_bot0
    ,sum(CASE WHEN u.bot_rt_network=1       THEN uf.status_count END) as count_bot1
    ,sum(CASE WHEN u.opinion_community=0    THEN uf.status_count END) as count_op0
    ,sum(CASE WHEN u.opinion_community=1    THEN uf.status_count END) as count_op1


    ,avg(CASE WHEN u.is_bot=true            THEN uf.avg_fact_score END) as fact_bot
    ,avg(CASE WHEN u.is_bot=false           THEN uf.avg_fact_score END) as fact_human
    ,avg(CASE WHEN u.is_q=true              THEN uf.avg_fact_score END) as fact_q
    ,avg(CASE WHEN u.is_q=false             THEN uf.avg_fact_score END) as fact_nonq
    ,avg(CASE WHEN u.bot_rt_network=0       THEN uf.avg_fact_score END) as fact_bot0
    ,avg(CASE WHEN u.bot_rt_network=1       THEN uf.avg_fact_score END) as fact_bot1
    ,avg(CASE WHEN u.opinion_community=0    THEN uf.avg_fact_score END) as fact_op0
    ,avg(CASE WHEN u.opinion_community=1    THEN uf.avg_fact_score END) as fact_op1



FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u
JOIN `tweet-collector-py.impeachment_production.recollected_user_fact_scores` uf ON u.user_id = uf.user_id
```


Group	| Status Count	| Avg Fact Score
--- | --- | ---
Anti-Trump	| 667,327	|3.727
Humans	| 669,840	| 3.329
Non-Q	| 890,604	| 3.325
Anti-Trump Bots	| 20,162	| 3.303
Bots	| 241,873	| 2.912
Pro-Trump	| 244,386	| 2.328
Pro-Trump Bots	| 597	| 2.171
Q	| 21,109	| 2.121

## More Migrations

Creating an updated version of the (slim) user details table, to include toxicity scores and news fact-check scores...

```sql
SELECT count(distinct user_id) as user_count
--FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u -- 3,600,545
--FROM `tweet-collector-py.impeachment_production.user_toxicity_scores` utox -- 3,600,545
--FROM `tweet-collector-py.impeachment_production.recollected_statuses` rs -- 2,360,104
FROM `tweet-collector-py.impeachment_production.recollected_user_fact_scores` uf -- 218,417
```



```sql
SELECT  count(distinct rs.user_id) as user_count
FROM`tweet-collector-py.impeachment_production.recollected_statuses` rs -- 2,360,104
LEFT JOIN `tweet-collector-py.impeachment_production.user_details_v6_slim` u ON u.user_id = rs.user_id
WHERE u.user_id IS NULL -- 67,476
```

There are 67K recollected users (i.e. authors of retweet targets) who aren't in our original user set. For now we can leave these out, but it would be more ideal to union them, but we don't have any user details for them at this point. So yeah, leave out for now.


```sql

DROP TABLE IF EXISTS `tweet-collector-py.impeachment_production.user_details_v20210806_slim`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.user_details_v20210806_slim` as (
   SELECT
      u.user_id
      ,u.created_on
      ,u.screen_name_count	,u.screen_names
      ,u.is_bot ,u.bot_rt_network
      ,u.is_q ,u.q_status_count
      ,u.status_count,u.rt_count
      ,u.avg_score_lr ,u.avg_score_nb ,u.avg_score_bert ,u.opinion_community
      ,u.follower_count	,u.follower_count_b	,u.follower_count_h
      ,u.friend_count ,u.friend_count_b ,u.friend_count_h

      --,utox.status_count as tox_scored_count
      ,round(utox.avg_toxicity, 8) as avg_toxicity
      ,round(utox.avg_severe_toxicity, 8) as avg_severe_toxicity
      ,round(utox.avg_insult, 8) as avg_insult
      ,round(utox.avg_obscene, 8) as avg_obscene
      ,round(utox.avg_threat, 8) as avg_threat
      ,round(utox.avg_identity_hate, 8) as avg_identity_hate

      ,coalesce(ufn.status_count, 0) as fact_scored_count
      ,round(ufn.avg_fact_score, 8) as avg_fact_score

   FROM `tweet-collector-py.impeachment_production.user_details_v6_slim` u
   LEFT JOIN `tweet-collector-py.impeachment_production.user_toxicity_scores` utox ON utox.user_id = u.user_id
   LEFT JOIN  `tweet-collector-py.impeachment_production.recollected_user_fact_scores` ufn on ufn.user_id = u.user_id

   --LIMIT 10
)
```

Warehouse migration:

```sql
DROP TABLE IF EXISTS `tweet-research-shared.impeachment_2020.user_details_v20210806_slim`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.user_details_v20210806_slim` as (
    SELECT *
    FROM `tweet-collector-py.impeachment_production.user_details_v20210806_slim`
);

```
