

# API Endpoints (Version 0)

Production API URL: https://impeachment-tweet-analysis-api.herokuapp.com/

## User Details

  + `GET /api/v0/user_details/<screen_name>`
  + `GET /api/v0/user_details/politico`

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

## User Tweets

  + `GET /api/v0/user_tweets/<screen_name>`
  + `GET /api/v0/user_tweets/berniesanders`

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

## Users Most Retweeted

Params:
  + `metric`: whether to calculate top users based on "retweet_count" or "retweeter_count" (default: "retweet_count")
  + `limit`: the number of top users for each community (default: 25,  max: 1000)

Request Examples:

  + `GET /api/v0/users_most_retweeted`
  + `GET /api/v0/users_most_retweeted?limit=5`
  + `GET /api/v0/users_most_retweeted?limit=5&metric=retweet_count`

Returns a list of top user objects:

```json
[
  {"community_id":1, "retweet_count":9223,  "retweeted_user_screen_name":"REALDONALDTRUMP", "retweeter_count":110},
  {"community_id":1, "retweet_count":3602,  "retweeted_user_screen_name":"CHARLIEKIRK11",   "retweeter_count":104},
  {"community_id":1, "retweet_count":2194,  "retweeted_user_screen_name":"MARKLEVINSHOW",   "retweeter_count":105},
  {"community_id":1, "retweet_count":2137,  "retweeted_user_screen_name":"DBONGINO",        "retweeter_count":102},
  {"community_id":1, "retweet_count":1454,  "retweeted_user_screen_name":"RUDYGIULIANI",    "retweeter_count":107},

  {"community_id":0, "retweet_count":27236, "retweeted_user_screen_name":"TRIBELAW",        "retweeter_count":567},
  {"community_id":0, "retweet_count":19708, "retweeted_user_screen_name":"JOYCEWHITEVANCE", "retweeter_count":563},
  {"community_id":0, "retweet_count":16831, "retweeted_user_screen_name":"KYLEGRIFFIN1",    "retweeter_count":563},
  {"community_id":0, "retweet_count":11871, "retweeted_user_screen_name":"NEAL_KATYAL",     "retweeter_count":560},
  {"community_id":0, "retweet_count":5824,  "retweeted_user_screen_name":"REPADAMSCHIFF",   "retweeter_count":567}
]
```

> NOTE: both metrics are provided in the response, but only the requested metric was used to calculate the "top" users, so only create a chart based on the requested metric (OK to provide the other one as context, for example in a tooltip or hover)

> NOTE: results may not be sorted

## Statuses Most Retweeted

Params:
  + `metric`: whether to calculate top statuses based on "retweet_count" or "retweeter_count" (default: "retweet_count")
  + `limit`: the number of top users for each community (default: 25,  max: 1000)

Request Examples:

  + `GET /api/v0/statuses_most_retweeted`
  + `GET /api/v0/statuses_most_retweeted?limit=3`
  + `GET /api/v0/statuses_most_retweeted?limit=3&metric=retweet_count`

Returns a list of top retweeted status objects:

```json
[
  {"community_id": 1, "retweet_count": 134, "retweeted_user_screen_name": "RUDYGIULIANI", "retweeter_count":82,
    "status_text": "RT @RudyGiuliani: Budapest | Kiev | Vienna  After hundreds of hours &amp; months of research, I have garnered witnesses &amp; documents which revea\u2026"},

  {"community_id": 1, "retweet_count": 135, "retweeted_user_screen_name": "GREGGJARRETT", "retweeter_count":66,
    "status_text": "RT @GreggJarrett: This entire impeachment process has been the true 'abuse of power' for political gain by the Democrats and especially Nan\u2026"},

  {"community_id": 1, "retweet_count": 146, "retweeted_user_screen_name": "DONALDJTRUMPJR", "retweeter_count":33,
    "status_text": "RT @DonaldJTrumpJr: Pelosi ripped up @realDonaldTrump's speech last night.  In that speech were stories of American Heroes &amp; American Dream\u2026"},

  {"community_id": 0, "retweet_count": 422, "retweeted_user_screen_name": "TRIBELAW", "retweeter_count":412,
    "status_text": "RT @tribelaw: When the Chief Justice administers the oath of impartiality to a Senator who has said he will not be impartial, he will need\u2026"},

  {"community_id": 0, "retweet_count": 424, "retweeted_user_screen_name": "REPADAMSCHIFF", "retweeter_count":384,
    "status_text": "RT @RepAdamSchiff: Impeachment of a president is a serious undertaking.   The Senate\u2019s role is to act as an impartial jury and provide a fa\u2026"},

  {"community_id": 0, "retweet_count": 434, "retweeted_user_screen_name": "REPADAMSCHIFF", "retweeter_count":420,
    "status_text": "RT @RepAdamSchiff: First, Trump said he wanted a trial in the Senate.  Then, he said he wanted to hear from witnesses.  Now, he wants the c\u2026"}

]
```

> NOTE: both metrics are provided in the response, but only the requested metric was used to calculate the "top" statuses, so only create a chart based on the requested metric (OK to provide the other one as context, for example in a tooltip or hover)

> NOTE: results may not be sorted

## Top Topics

Params:
  + `limit`: the number of top users for each community (default: 25,  max: 1000)

Request Examples:

  + `GET /api/v0/top_topics`
  + `GET /api/v0/top_topics?limit=3`

Returns a list of top topic objects for each community:

```json
[
  {"community_id": 0, "token": "", }



```
