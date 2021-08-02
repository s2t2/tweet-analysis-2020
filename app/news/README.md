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


Uploading a table of fact check scores from [CSV file](data/domain_fact_scores.csv) to `domain_fact_scores` table...
