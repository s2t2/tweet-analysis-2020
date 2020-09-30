

# API Endpoints (Version 0)

Production API URL: https://impeachment-tweet-analysis-api.herokuapp.com/

> GENERAL NOTES FOR ALL ENDPOINTS:
>
>   + results are returned in no particular order (to reduce query times), so it is the client's responsibility to sort them as desired

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

## Top Profile Tokens

Params:
  + `limit`: the number of top tokens for each community (default: 20, suggested max: 25)

Request Examples:

  + `GET /api/v0/top_profile_tokens`
  + `GET /api/v0/top_profile_tokens?limit=3`

Returns a list of top profile token objects for each community:

```json
[
    {"community_id":1, "count":48,"pct":0.037296037296037296,"rank":1,"token":"maga"},
    {"community_id":1, "count":27,"pct":0.02097902097902098,"rank":2,"token":"trump"},
    {"community_id":1, "count":21,"pct":0.016317016317016316,"rank":3,"token":"kag"},
    {"community_id":1, "count":18,"pct":0.013986013986013986,"rank":4,"token":"conservative"},
    {"community_id":1, "count":14,"pct":0.010878010878010878,"rank":5,"token":"god"},
    {"community_id":1, "count":12,"pct":0.009324009324009324,"rank":6,"token":"proud"},
    {"community_id":1, "count":12,"pct":0.009324009324009324,"rank":7,"token":"trump2020"},
    {"community_id":1, "count":12,"pct":0.009324009324009324,"rank":8,"token":"married"},
    {"community_id":1, "count":11,"pct":0.008547008547008548,"rank":9,"token":"love"},
    {"community_id":1, "count":10,"pct":0.00777000777000777,"rank":10,"token":"patriot"},
    {"community_id":1, "count":10,"pct":0.00777000777000777,"rank":11,"token":"2020"},
    {"community_id":1, "count":9,"pct":0.006993006993006993,"rank":12,"token":"country"},
    {"community_id":1, "count":9,"pct":0.006993006993006993,"rank":13,"token":"nra"},
    {"community_id":1, "count":9,"pct":0.006993006993006993,"rank":14,"token":"2a"},
    {"community_id":1, "count":8,"pct":0.006216006216006216,"rank":15,"token":"family"},
    {"community_id":1, "count":8,"pct":0.006216006216006216,"rank":16,"token":"wwg1wga"},
    {"community_id":1, "count":7,"pct":0.005439005439005439,"rank":17,"token":"q"},
    {"community_id":1, "count":6,"pct":0.004662004662004662,"rank":18,"token":"christian"},
    {"community_id":1, "count":6,"pct":0.004662004662004662,"rank":19,"token":"genflynn"},
    {"community_id":1, "count":6,"pct":0.004662004662004662,"rank":20,"token":"draintheswamp"},

    {"community_id":0, "count":66,"pct":0.012050392550666424,"rank":1,"token":"resist"},
    {"community_id":0, "count":47,"pct":0.008581340149716999,"rank":2,"token":"trump"},
    {"community_id":0, "count":42,"pct":0.00766843162315136,"rank":3,"token":"retired"},
    {"community_id":0, "count":37,"pct":0.006755523096585722,"rank":4,"token":"resistance"},
    {"community_id":0, "count":36,"pct":0.006572941391272595,"rank":5,"token":"love"},
    {"community_id":0, "count":33,"pct":0.006025196275333212,"rank":6,"token":"theresistance"},
    {"community_id":0, "count":31,"pct":0.005660032864706956,"rank":7,"token":"blue"},
    {"community_id":0, "count":28,"pct":0.005112287748767573,"rank":8,"token":"proud"},
    {"community_id":0, "count":28,"pct":0.005112287748767573,"rank":9,"token":"dms"},
    {"community_id":0, "count":27,"pct":0.004929706043454446,"rank":10,"token":"vote"},
    {"community_id":0, "count":27,"pct":0.004929706043454446,"rank":11,"token":"mom"},
    {"community_id":0, "count":25,"pct":0.0045645426328281904,"rank":12,"token":"lover"},
    {"community_id":0, "count":23,"pct":0.004199379222201935,"rank":13,"token":"people"},
    {"community_id":0, "count":22,"pct":0.004016797516888808,"rank":14,"token":"democrat"},
    {"community_id":0, "count":21,"pct":0.00383421581157568,"rank":15,"token":"mother"},
    {"community_id":0, "count":20,"pct":0.0036516341062625525,"rank":16,"token":"fbr"},
    {"community_id":0, "count":19,"pct":0.003469052400949425,"rank":17,"token":"liberal"},
    {"community_id":0, "count":19,"pct":0.003469052400949425,"rank":18,"token":"impeach"},
    {"community_id":0, "count":18,"pct":0.0032864706956362974,"rank":19,"token":"progressive"},
    {"community_id":0, "count":18,"pct":0.0032864706956362974,"rank":20,"token":"gop"}
]
```

> NOTES:
>
>   + "count" is the number of bots in that community who included the token in their profile
>   + "pct" is the percentage of users who included the token in their profile
>   + prefer to use the relative "pct" instead of raw "count" when graphing

## Top Profile Tags

Params:
  + `limit`: the number of top hashtags for each community (default: 20, max: 20)

Request Examples:

  + `GET /api/v0/top_profile_tags`
  + `GET /api/v0/top_profile_tags?limit=3`

Returns a list of top profile hashtag objects for each community:

```json
[
    {"community_id": 0, "count":58,"pct":0.0777479892761394,"rank":1,"token":"#RESIST"},
    {"community_id": 0, "count":33,"pct":0.04423592493297587,"rank":2,"token":"#THERESISTANCE"},
    {"community_id": 0, "count":27,"pct":0.036193029490616625,"rank":3,"token":"#RESISTANCE"},
    {"community_id": 0, "count":19,"pct":0.02546916890080429,"rank":4,"token":"#FBR"},
    {"community_id": 0, "count":16,"pct":0.021447721179624665,"rank":5,"token":"#VOTEBLUENOMATTERWHO"},
    {"community_id": 0, "count":10,"pct":0.013404825737265416,"rank":6,"token":"#VOTEBLUE"},
    {"community_id": 0, "count":9,"pct":0.012064343163538873,"rank":7,"token":"#BLUEWAVE2020"},
    {"community_id": 0, "count":8,"pct":0.010723860589812333,"rank":8,"token":"#IMPEACHTRUMP"},
    {"community_id": 0, "count":8,"pct":0.010723860589812333,"rank":9,"token":"#BIDEN2020"},
    {"community_id": 0, "count":7,"pct":0.00938337801608579,"rank":10,"token":"#IMPEACHTRUMPNOW"},
    {"community_id": 0, "count":6,"pct":0.00804289544235925,"rank":11,"token":"#METOO"},
    {"community_id": 0, "count":6,"pct":0.00804289544235925,"rank":12,"token":"#IMPEACH"},
    {"community_id": 0, "count":6,"pct":0.00804289544235925,"rank":13,"token":"#BLUEWAVE"},
    {"community_id": 0, "count":6,"pct":0.00804289544235925,"rank":14,"token":"#VOTEBLUE2020"},
    {"community_id": 0, "count":5,"pct":0.006702412868632708,"rank":15,"token":"#WTP2020"},
    {"community_id": 0, "count":5,"pct":0.006702412868632708,"rank":16,"token":"#BLM"},
    {"community_id": 0, "count":5,"pct":0.006702412868632708,"rank":17,"token":"#IMPEACHANDREMOVE"},
    {"community_id": 0, "count":5,"pct":0.006702412868632708,"rank":18,"token":"#RESISTER"},
    {"community_id": 0, "count":5,"pct":0.006702412868632708,"rank":19,"token":"#IMPOTUS"},
    {"community_id": 0, "count":5,"pct":0.006702412868632708,"rank":20,"token":"#NOTMYPRESIDENT"},

    {"community_id": 1, "count":32,"pct":0.14953271028037382,"rank":1,"token":"#MAGA"},
    {"community_id": 1, "count":14,"pct":0.06542056074766354,"rank":2,"token":"#KAG"},
    {"community_id": 1, "count":12,"pct":0.056074766355140186,"rank":3,"token":"#TRUMP2020"},
    {"community_id": 1, "count":7,"pct":0.03271028037383177,"rank":4,"token":"#2A"},
    {"community_id": 1, "count":6,"pct":0.028037383177570093,"rank":5,"token":"#DRAINTHESWAMP"},
    {"community_id": 1, "count":5,"pct":0.02336448598130841,"rank":6,"token":"#PATRIOT"},
    {"community_id": 1, "count":5,"pct":0.02336448598130841,"rank":7,"token":"#DEPLORABLE"},
    {"community_id": 1, "count":5,"pct":0.02336448598130841,"rank":8,"token":"#NRA"},
    {"community_id": 1, "count":5,"pct":0.02336448598130841,"rank":9,"token":"#WWG1WGA"},
    {"community_id": 1, "count":4,"pct":0.018691588785046728,"rank":10,"token":"#AMERICAFIRST"},
    {"community_id": 1, "count":4,"pct":0.018691588785046728,"rank":11,"token":"#TRUMPTRAIN"},
    {"community_id": 1, "count":4,"pct":0.018691588785046728,"rank":12,"token":"#CONSERVATIVE"},
    {"community_id": 1, "count":3,"pct":0.014018691588785047,"rank":13,"token":"#VETERAN"},
    {"community_id": 1, "count":3,"pct":0.014018691588785047,"rank":14,"token":"#TRUMP"},
    {"community_id": 1, "count":3,"pct":0.014018691588785047,"rank":15,"token":"#1A"},
    {"community_id": 1, "count":2,"pct":0.009345794392523364,"rank":16,"token":"#BUILDTHEWALL"},
    {"community_id": 1, "count":2,"pct":0.009345794392523364,"rank":17,"token":"#WALKAWAY"},
    {"community_id": 1, "count":2,"pct":0.009345794392523364,"rank":18,"token":"#THEGREATAWAKENING"},
    {"community_id": 1, "count":2,"pct":0.009345794392523364,"rank":19,"token":"#BUILDKATESWALL"},
    {"community_id": 1, "count":2,"pct":0.009345794392523364,"rank":20,"token":"#QANON"}
]
```

> NOTES:
>
>   + "token" is the hashtag
>   + "count" is the number of bots in that community who included the hashtag in their profile
>   + "pct" is the percentage of users who included the hashtag in their profile
>   + prefer to use the relative "pct" instead of raw "count" when graphing

## Top Status Tokens

Params:
  + `limit`: the number of top tokens for each community (default: 50, suggested max if you want to remove stopwords: 250)

Request Examples:

  + `GET /api/v0/top_status_tokens`
  + `GET /api/v0/top_status_tokens?limit=3`

Returns a list of top status token objects for each community:

```json
[
  {"community_id":0,"count":2695236,"doc_count":2556291,"doc_pct":0.4566554510611654,"pct":0.04457294809118552,"rank":1,"token":"impeach"},
  {"community_id":0,"count":1921904,"doc_count":1757316,"doc_pct":0.31392667369912225,"pct":0.031783831630418195,"rank":2,"token":"trump"},
  {"community_id":0,"count":667867,"doc_count":642424,"doc_pct":0.11476252957606083,"pct":0.011044970133530348,"rank":3,"token":"trial"},
  {"community_id":0,"count":509971,"doc_count":490615,"doc_pct":0.08764339197782008,"pct":0.008433736752926264,"rank":4,"token":"senate"},
  {"community_id":0,"count":428081,"doc_count":405354,"doc_pct":0.07241237938460357,"pct":0.007079466210685368,"rank":5,"token":"house"},

  {"community_id":1,"count":4713355,"doc_count":4485176,"doc_pct":0.5307376135020977,"pct":0.05210428814735738,"rank":1,"token":"impeach"},
  {"community_id":1,"count":1662904,"doc_count":1570930,"doc_pct":0.18589050667774248,"pct":0.01838275054125844,"rank":2,"token":"trump"},
  {"community_id":1,"count":1610886,"doc_count":1536584,"doc_pct":0.18182629290478397,"pct":0.017807711983617604,"rank":3,"token":"democrat"},
  {"community_id":1,"count":1317077,"doc_count":1310882,"doc_pct":0.15511863620577138,"pct":0.014559768895034858,"rank":4,"token":"realdonaldtrump"},
  {"community_id":1,"count":1118666,"doc_count":1076259,"doc_pct":0.12735534417604888,"pct":0.012366413224688507,"rank":5,"token":"pelosi"}
]
```

> NOTES:
>
>   + "count" and "pct" refer to token counts
>   + "doc_count" and "doc_pct" refer to tweet counts
>   + ok to use relative percentages and/or raw counts when graphing

## Top Status Tags

Params:
  + `limit`: the number of top hashtags for each community (default: 50, suggested max if you want to remove stopwords: 250)

Request Examples:

  + `GET /api/v0/top_status_tags`
  + `GET /api/v0/top_status_tags?limit=5`

Returns a list of top status hashtag objects for each community:

```json
[
  {"community_id":1,"count":127560,"doc_count":127437,"doc_pct":0.015079811639914873,"pct":0.07399149179051753,"rank":1,"token":"#IMPEACHMENT"},
  {"community_id":1,"count":62241,"doc_count":62184,"doc_pct":0.0073583261299031396,"pct":0.03610304515940422,"rank":2,"token":"#FACTSMATTER"},
  {"community_id":1,"count":51834,"doc_count":51320,"doc_pct":0.006072772690509281,"pct":0.03006643920876204,"rank":3,"token":"#QANON"},
  {"community_id":1,"count":39978,"doc_count":39893,"doc_pct":0.004720598615403093,"pct":0.023189337243660315,"rank":4,"token":"#WWG1WGA"},
  {"community_id":1,"count":31590,"doc_count":31447,"doc_pct":0.0037211707482160046,"pct":0.01832385720964604,"rank":5,"token":"#TRUMP2020"},

  {"community_id":0,"count":97178,"doc_count":95719,"doc_pct":0.017099228186510725,"pct":0.062029724837167025,"rank":1,"token":"#MOSCOWMITCH"},
  {"community_id":0,"count":57989,"doc_count":57657,"doc_pct":0.010299838062972334,"pct":0.03701497986769103,"rank":2,"token":"#IMPEACHMENT"},
  {"community_id":0,"count":44227,"doc_count":42679,"doc_pct":0.007624170329528007,"pct":0.028230552598050854,"rank":3,"token":"#GOPCOVERUP"},
  {"community_id":0,"count":38227,"doc_count":37018,"doc_pct":0.006612890115946197,"pct":0.02440069039649287,"rank":4,"token":"#25THAMENDMENTNOW"},
  {"community_id":0,"count":31643,"doc_count":31254,"doc_pct":0.00558320999740079,"pct":0.0201980549406499,"rank":5,"token":"#IMPOTUS"}
]
```

> NOTES:
>
>   + "count" and "pct" refer to token counts
>   + "doc_count" and "doc_pct" refer to tweet counts
>   + ok to use relative percentages and/or raw counts when graphing
