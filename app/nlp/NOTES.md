
## Pg Queries

```sql
SELECT
  status_id
  ,count(distinct status_text) as text_count
FROM tweets
GROUP BY 1
HAVING count(distinct status_text) > 1
-- returns no rows
```

## Pg Migrations

Use the PG Pipeline to download the "tweets" table. Then migrate a "statuses" table:

```sql
DROP TABLE IF EXISTS statuses;
CREATE TABLE statuses as (
  SELECT DISTINCT status_id, user_id, status_text, created_at
  FROM tweets
);
ALTER TABLE table_name ADD PRIMARY KEY (status_id);
CREATE INDEX status_index_user_id ON statuses (user_id);
CREATE INDEX status_index_created_at ON statuses (created_at);
```


```sql
DROP TABLE IF EXISTS basilica_embeddings;
CREATE TABLE basilica_embeddings (
    status_id int8 PRIMARY KEY,
    user_id int8,
    embedding JSONB
);
CREATE INDEX bas_index_uid ON basilica_embeddings (user_id);
```
