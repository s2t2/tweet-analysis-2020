
# API

## Usage

```sh
FLASK_APP="api" flask run
```

## Endpoints (Version 0)

### User Details

  + `GET /api/v0/user_details/<screen_name>`

Returns:

```json
{
  "screen_name_count":1,
  "screen_names":"POLITICO",
  "tweet_count":668,
  "user_created_at":"Mon, 08 Oct 2007 00:29:38 GMT",
  "user_descriptions":"NOBODY KNOWS POLITICS LIKE POLITICO. GOT A NEWS TIP FOR US?  \ud83d\udc49 HTTPS://POLITI.CO/2LCOTT5",
  "user_id":9300262,
  "user_names":"POLITICO"
}
```
