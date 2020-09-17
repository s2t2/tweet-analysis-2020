
# API

## Usage

```sh
FLASK_APP="api" flask run
```

## Endpoints (Version 0)

### User Details

  + `GET /api/v0/user_details/<screen_name>`

Returns user object:

```json
{
  "screen_name_count": 1,
  "screen_names": "POLITICO",
  "tweet_count": 668,
  "user_created_at": "Mon, 08 Oct 2007 00:29:38 GMT",
  "user_descriptions": "NOBODY KNOWS POLITICS LIKE POLITICO. GOT A NEWS TIP FOR US?  \ud83d\udc49 HTTPS://POLITI.CO/2LCOTT5",
  "user_id": 9300262,
  "user_names": "POLITICO"
}
```

### User Tweets

  + `GET /api/v0/user_tweets/<screen_name>`

Returns list of tweet objects:

```json
[
  {
    "created_at":"Wed, 22 Jan 2020 01:08:33 GMT",
    "opinion_score":1,
    "status_id":"1219788909678383105",
    "status_text":"RT @AOC: \u201cNot me, Us\u201d means building a mass movement for social, economic, and racial justice.  And movement means we carry and care for on\u2026"
  },
  {
    "created_at":"Fri, 07 Feb 2020 01:27:01 GMT",
    "opinion_score":0,
    "status_id":"1225591763840196608",
    "status_text":"What did Trump learn from the impeachment trial? He learned he can get away with corruption, with continuing to lie, with considering himself above the law. https://t.co/nbGh45lneg"
  },
  {
    "created_at":"Fri, 17 Jan 2020 22:46:26 GMT",
    "opinion_score":0,
    "status_id":"1218303595612950530",
    "status_text":"Let\u2019s be clear about who is rigging what: it is Donald Trump\u2019s action to use the power of the federal government for his own political benefit that is the cause of the impeachment trial. Democrats are going to unite to sweep him out of the White House in November."
  },
  {
    "created_at":"Fri, 24 Jan 2020 22:38:19 GMT",
    "opinion_score":0,
    "status_id":"1220838266389266434",
    "status_text":"I may be stuck in Washington for Trump's impeachment trial, but this is what \"Not Me, Us\" is all about.  There are hundreds of events you can join across the country to support our campaign.  Help us keep the ball rolling and sign up at https://t.co/0gzurtl5gF. https://t.co/tLkZbyKRCK"
  },
  {
    "created_at":"Wed, 05 Feb 2020 02:35:59 GMT",
    "opinion_score":0,
    "status_id":"1224884343606333443",
    "status_text":"Tomorrow the votes may not be there to impeach Trump. But I'm absolutely confident that in November the votes will be there to beat Donald Trump."
  }
]
```
