# Natural Language Processing

We can use multiple approaches for training our classifiers - fetching tweet embeddings from an external API, or creating our own.

## Basilica Embeddings

Run the basilica service to test the credentials:

```sh
python -m app.basilica_service
```

Then fetch embeddings for each status text and store them in an "embeddings" table on BigQuery:

```sh
python -m app.nlp.fetch_basilica_embeddings
```
