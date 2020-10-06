# Notes

## Data Labeling

Since the same status text can be retweeted by many users and the resulting retweet text will be the same,
 we need to remove duplicate statuses from the training data, to prevent model over-fitting.

Originally we were thinking just de-dup the statuses, but when a status is repeated and is retweeted by members of the same community, we could perhaps drop the status, but why don't we take the mean community score, to give the status a more accurate label than just the normal 0 or 1 from earlier. So let's roll with this...

```sql
CREATE TABLE impeachment_production.2_community_labeled_status_texts as (
  SELECT
    status_text
    ,count(distinct status_id) as status_occurrences
    ,avg(community_id) as avg_community_score
    -- TODO maybe add the median or mode community score as well
  FROM impeachment_production.2_community_labeled_tweets
  GROUP BY 1
  -- HAVING status_occurrences > 1 and avg_community_score between 0.3 and 0.7
  -- ORDER BY 2 DESC
) -- 2,771,905 tweets
```
