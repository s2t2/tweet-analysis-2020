# Bot Communities

## Tableau Workbooks

For each k-communities table (i.e. "2_bot_communities", "3_bot_communities", etc.), execute the following query and export to CSV:

```sql
SELECT
  bc.community_id

  ,ud.user_id
  ,ud.screen_name_count as user_screen_name_count
  ,ARRAY_TO_STRING(ud.screen_names, ' | ')  as user_screen_names
  ,rt.user_created_at

  ,rt.retweeted_user_id
  ,rt.retweeted_user_screen_name

  ,rt.status_id
  --,rt.status_text
  ,rt.created_at as status_created_at

FROM impeachment_production.2_bot_communities bc -- 681
JOIN impeachment_production.user_details_v2 ud on cast(ud.user_id  as int64) = bc.user_id
JOIN impeachment_production.retweets_v2 rt on rt.user_id = bc.user_id
```

Then import that CSV into a new Tableau Workbook...

Actually the downloads might be too big. Writing a download script instead...
