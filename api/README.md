
# API

## Usage

Run a development API server on port 5000:

```sh
FLASK_APP="api" flask run
```

Or use the production API server: https://impeachment-tweet-analysis-api.herokuapp.com/

## [Documentation (Version 0)](/api/docs/endpoints-v0.md)

## [Documentation (Version 1)](/api/docs/endpoints-v1.md)

## Testing

```sh
APP_ENV="test" pytest test/test_api_v0.py

APP_ENV="test" pytest test/test_api_v1.py
```
