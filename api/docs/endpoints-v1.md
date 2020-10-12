

# API Endpoints (Version 1)

Production API URL: https://impeachment-tweet-analysis-api.herokuapp.com/

> GENERAL NOTES FOR ALL ENDPOINTS:
>
>   + results are returned in no particular order (to reduce query times), so it is the client's responsibility to sort them as desired

## User Tweets

  + `GET /api/v1/user_tweets/<screen_name>`
  + `GET /api/v1/user_tweets/berniesanders`

Returns list of tweet objects, with opinion scores for each:

```json
[
  {
    "created_at":"Wed, 05 Feb 2020 02:35:59 GMT",
    "prediction_bert":null,
    "prediction_lr":"D",
    "prediction_nb":"D",
    "score_bert":null,
    "score_lr":0,
    "score_nb":0,
    "status_id":"1224884343606333443",
    "status_text":"Tomorrow the votes may not be there to impeach Trump. But I'm absolutely confident that in November the votes will be there to beat Donald Trump."
  },
  {
    "created_at":"Fri, 07 Feb 2020 01:27:01 GMT",
    "prediction_bert":null,
    "prediction_lr":"D",
    "prediction_nb":"D",
    "score_bert":null,
    "score_lr":0,
    "score_nb":0,
    "status_id":"1225591763840196608",
    "status_text":"What did Trump learn from the impeachment trial? He learned he can get away with corruption, with continuing to lie, with considering himself above the law. https://t.co/nbGh45lneg"
  },
  {
    "created_at":"Sat, 25 Jan 2020 21:37:57 GMT",
    "prediction_bert":null,
    "prediction_lr":"R",
    "prediction_nb":"D",
    "score_bert":null,
    "score_lr":1,
    "score_nb":0,
    "status_id":"1221185462993330183",
    "status_text":"RT @BNeidhardt: UPDATE: @BernieSanders is joining @AOC &amp; @MMFlint at tonight's rallly in Marshalltown https://t.co/NQIBxlcVeJ"
  },
  {
    "created_at":"Fri, 24 Jan 2020 22:38:19 GMT",
    "prediction_bert":null,
    "prediction_lr":"D",
    "prediction_nb":"D",
    "score_bert":null,
    "score_lr":0,
    "score_nb":0,
    "status_id":"1220838266389266434",
    "status_text":"I may be stuck in Washington for Trump's impeachment trial, but this is what \"Not Me, Us\" is all about.  There are hundreds of events you can join across the country to support our campaign.  Help us keep the ball rolling and sign up at https://t.co/0gzurtl5gF. https://t.co/tLkZbyKRCK"
  },
  {
    "created_at":"Fri, 17 Jan 2020 22:46:26 GMT",
    "prediction_bert":null,
    "prediction_lr":"D",
    "prediction_nb":"D",
    "score_bert":null,
    "score_lr":0,
    "score_nb":0,
    "status_id":"1218303595612950530",
    "status_text":"Let\u2019s be clear about who is rigging what: it is Donald Trump\u2019s action to use the power of the federal government for his own political benefit that is the cause of the impeachment trial. Democrats are going to unite to sweep him out of the White House in November."
  }
]
```


> NOTES:
>
>   + "prediction_" attributes will be either "D" or "R"
>   + "score_" attributes will be either 0 or 1. average these on the client side to get the mean opinion score for that user!
>   + "_lr" attributes refer to the best Logistic Regression Model (id: `2020-10-07-0220`)
>   + "_lr" attributes refer to the best Multinomial Naive Bayes Model (id: `2020-10-07-0222`)
>   + "_bert" attributes refer to the best BERT Transformer Model (not yet available but will show up when it is available)

## Users Most Followed


  + `GET /api/v1/users_most_followed`
  + `GET /api/v1/users_most_followed?limit=10`

Params:
  + `limit`: specifies the number of top users to return (default: 500, max: 1000)

Returns list of user objects, with mean opinion scores and other aggregated metrics:

```json
[
  {"avg_score_lr":0.877,"avg_score_nb":0.877,"category":"ELECTED-OFFICIAL","follower_count":1161079,"screen_name":"REALDONALDTRUMP","status_count":374},
  {"avg_score_lr":0.25,"avg_score_nb":0.25,"category":"ELECTED-OFFICIAL","follower_count":794618,"screen_name":"AOC","status_count":4},
  {"avg_score_lr":0.7838,"avg_score_nb":0.7838,"category":null,"follower_count":790014,"screen_name":"POTUS","status_count":74},
  {"avg_score_lr":0.0,"avg_score_nb":0.0,"category":"ELECTED-OFFICIAL","follower_count":657448,"screen_name":"HILLARYCLINTON","status_count":6},
  {"avg_score_lr":0.2308,"avg_score_nb":0.2308,"category":"MAJOR-MEDIA-OUTLET","follower_count":604397,"screen_name":"NYTIMES","status_count":312},
  {"avg_score_lr":0.2222,"avg_score_nb":0.2222,"category":"ELECTED-OFFICIAL","follower_count":601848,"screen_name":"BERNIESANDERS","status_count":9},
  {"avg_score_lr":0.7602,"avg_score_nb":0.7602,"category":null,"follower_count":596627,"screen_name":"WHITEHOUSE","status_count":196},
  {"avg_score_lr":0.0,"avg_score_nb":0.0,"category":"ELECTED-OFFICIAL","follower_count":567173,"screen_name":"SENSANDERS","status_count":6},
  {"avg_score_lr":0.2592,"avg_score_nb":0.2592,"category":"MAJOR-MEDIA-OUTLET","follower_count":554626,"screen_name":"CNN","status_count":652},
  {"avg_score_lr":0.069,"avg_score_nb":0.069,"category":"ELECTED-OFFICIAL","follower_count":550729,"screen_name":"SPEAKERPELOSI","status_count":29}
  ]
]
```

> NOTES:
>
>  + `follower_count` is: "the number of followers also talking about impeachment". the real follower counts are likely (much) higher than the numbers represented here.
>  + the query is guaranteed to return the top x users, but they may not be sorted when you get them. responsibility of client to sort
>  + `category` is a subjective label meant to help filter users for comparison. includes "ELECTED-OFFICIAL", "PARTY", and "MAJOR-MEDIA-OUTLET". NOTE: @FoxNews does not appear in the dataset because they tweet URLs only.
