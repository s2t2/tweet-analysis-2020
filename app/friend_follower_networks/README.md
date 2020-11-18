# Friend / Follower Networks


For active users only, with flags for bot, opinion community, q, etc.

```sql
DROP TABLE IF EXISTS impeachment_production.user_details_v5;
CREATE TABLE IF NOT EXISTS impeachment_production.user_details_v5 as (
  SELECT
    uf.user_id
    ,extract(date from ud.user_created_at) as created_on
    ,ud.screen_name_count
    ,ud.screen_names

    ,ud.is_bot
    ,ud.community_id as bot_network

    ,case when q.q_status_count > 0 then true else false end is_q
    ,q.q_status_count

    ,ud.status_count
    ,ud.rt_count

    ,ud.avg_score_lr
    ,ud.avg_score_nb
    ,ud.avg_score_bert
    ,cast(round(coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr)) as int64) as opinion_community

    ,uf.follower_count
    ,uf.follower_count_b
    ,uf.follower_count_h
    ,uf.follower_ids_b
    ,uf.follower_ids_h

  FROM impeachment_production.active_followers_bh_v2 uf
  JOIN impeachment_production.user_details_v4 ud ON ud.user_id = uf.user_id
  LEFT JOIN impeachment_production.q_users q ON q.user_id = uf.user_id
  WHERE coalesce(ud.avg_score_bert, ud.avg_score_nb, ud.avg_score_lr) <> 0.5
  --LIMIT 10
)

```
