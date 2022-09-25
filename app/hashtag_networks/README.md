
# Hashtag Co-occurance Networks


## Exploration

We are thankful for some existing clean hashtag tables, including a flattened version.

```sql
SELECT count(distinct user_id) as user_count
FROM `tweet-collector-py.impeachment_production.profile_tags_v2` -- 458,159
WHERE ARRAY_LENGTH(tags) > 0 -- 451,698
```

```sql
SELECT
    count(distinct user_id) as user_count  -- 451,698
    ,count(user_id) as row_count -- 1,776,409
    ,count(distinct upper(tag)) as tag_count -- 258,622
FROM `tweet-collector-py.impeachment_production.profile_tags_v2_flat`
```

The profile tags table has duplicate instances of the same tag (if collected at different times, so let's de-dupe):

```sql
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.profile_tags_v2_distinct` as (
  SELECT user_id, ARRAY_AGG(DISTINCT tag) as distinct_tags
  FROM `tweet-collector-py.impeachment_production.profile_tags_v2_flat`
  GROUP BY user_id
  -- LIMIT 10
)
```

## Plan

**Profile Hashtag Co-occurance Network**

We can make a normal / undirected graph, with the following characteristics:
  + Node per distinct hashtag (~250K nodes)
  + Node weight is the number of user profiles the hashtag appears in.
  + Edge between each co-occurance of hashtag pairs in a given user's profile
  + Edge weight as the number of user profiles that have a co-occurance of those hashtags.
  + Extra info for the edge, to store if possible, would be: the list of distinct user_ids who have those tags co-occuring.

## Usage

See [User Profile Hashtag Co-occurance Network notebook](/app/hashtag_networks/User_Profile_Hashtag_Co_occurance_Network.ipynb).
