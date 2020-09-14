# Deployment Instructions

Ensure Procfile contains:

```
web: gunicorn "api:create_app()"
```
