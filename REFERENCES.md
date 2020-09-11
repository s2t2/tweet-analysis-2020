# References

## Notebook Conversion

From Google Colab, select "File" > "Download .py" and store the resulting file in the "start" dir.

## Google BigQuery

Working with BigQuery:

  + https://cloud.google.com/bigquery/docs/reference/standard-sql/operators
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/conversion_rules
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions
  + https://cloud.google.com/dataprep/docs/html/DATEDIF-Function_57344707
  + https://towardsdatascience.com/google-bigquery-sql-dates-and-times-cheat-sheet-805b5502c7f0
  + https://cloud.google.com/bigquery/docs/running-queries#batch
  + https://cloud.google.com/bigquery/docs/paging-results
  + https://stackoverflow.com/a/27158310/670433
  + https://cloud.google.com/bigquery/docs/schemas
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#insert_statement
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#converting_arrays_to_strings
  + https://cloud.google.com/bigquery/docs/reference/rest/v2/tables/list
  + https://cloud.google.com/bigquery/docs/reference/rest/v2/tables/delete
  + https://stackoverflow.com/a/46012467/670433
  + https://vverma.net/querying-arrays-in-bigquery.html
  + https://stackoverflow.com/questions/53737407/resources-exceeded-bigquery/53739742
  + https://cloud.google.com/bigquery/docs/exporting-data#bigquery_extract_table_compressed-python


## Twitter Resources

Ad-hoc conversions between user ids and screen names:
  + https://tweeterid.com/

Working with the `twint` package:
  + https://github.com/twintproject/twint
  + https://pielco11.ovh/posts/twint-osint/#followersfollowing
  + https://github.com/twintproject/twint/pull/685
  + https://github.com/twintproject/twint/wiki/Storing-objects-in-RAM
  + https://github.com/twintproject/twint/issues/270
  + https://github.com/twintproject/twint/issues/704

## Threading in Python

Threads and Thread Pool Executors:

  + https://docs.python.org/3/library/threading.html
  + https://realpython.com/intro-to-python-threading/
  + https://pymotw.com/2/threading/
  + https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor

Locks and Semaphores:

  + https://docs.python.org/3.7/library/threading.html#threading.Lock
  + https://docs.python.org/3.7/library/threading.html#threading.Semaphore
  + https://docs.python.org/3.7/library/threading.html#threading.BoundedSemaphore
  + https://stackoverflow.com/questions/48971121/what-is-the-difference-between-semaphore-and-boundedsemaphore
  + https://www.pythonstudio.us/reference-2/semaphore-and-bounded-semaphore.html

## Threading on Heroku

  + https://stackoverflow.com/questions/38632621/can-i-run-multiple-threads-in-a-single-heroku-python-dyno
  + https://devcenter.heroku.com/articles/limits#processes-threads
  + https://devcenter.heroku.com/articles/dynos#process-thread-limits

## Networkx

  + https://networkx.github.io/
  + https://github.com/networkx/networkx
  + https://networkx.github.io/documentation/latest/
  + https://networkx.github.io/documentation/latest/tutorial.html
  + https://networkx.github.io/documentation/latest/reference/classes/digraph.html
  + https://networkx.github.io/documentation/latest/reference/readwrite/generated/networkx.readwrite.gpickle.read_gpickle.html
  + https://networkx.github.io/documentation/latest/reference/convert.html
  + https://networkx.github.io/documentation/latest/reference/generated/networkx.convert_matrix.from_pandas_edgelist.html
  + https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.algorithms.link_prediction.jaccard_coefficient.html

## Google Cloud Storage

  + https://dev.to/sethmlarson/python-data-streaming-to-google-cloud-storage-with-resumable-uploads-458h
  + https://github.com/zaman-lab/brexitmeter-py
  + https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
  + https://cloud.google.com/storage/docs/naming-objects
  + https://googleapis.dev/python/storage/latest/blobs.html
  + https://github.com/googleapis/python-storage/issues/74#issuecomment-603296568
  + https://googleapis.dev/python/storage/latest/buckets.html#google.cloud.storage.bucket.Bucket.copy_blob

## SQLAlchemy

  + https://docs.sqlalchemy.org/en/13/
  + https://docs.sqlalchemy.org/en/13/intro.html
  + https://docs.sqlalchemy.org/en/13/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg2
  + https://docs.sqlalchemy.org/en/13/core/type_basics.html
  + https://docs.sqlalchemy.org/en/13/core/metadata.html#creating-and-dropping-database-tables
  + https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html
  + https://stackoverflow.com/questions/45259764/how-to-create-a-single-table-using-sqlalchemy-declarative-base
  + https://www.compose.com/articles/using-postgresql-through-sqlalchemy/
  + https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/

## PostgreSQL

Big PG Data:

  + https://www.postgresqltutorial.com/postgresql-fetch/
  + https://www.buggycoder.com/fetching-millions-of-rows-in-python-psycopg2/

## MPI

  + https://mpi4py.readthedocs.io/en/stable/install.html
  + https://mpi4py.readthedocs.io/en/stable/tutorial.html?highlight=comm_world
  + https://mpi4py.readthedocs.io/en/stable/overview.html?highlight=intracomm#communicators

> In MPI for Python, MPI.Comm is the base class of communicators.
> The MPI.Intracomm and MPI.Intercomm classes are sublcasses of the MPI.Comm class.
>
> The two predefined intracommunicator instances are available: MPI.COMM_SELF and MPI.COMM_WORLD. From them, new communicators can be created as needed.

## General Tools

  + https://tabstospaces.com/
  + https://www.fileformat.info/info/unicode/char/0fffd/index.htm
  + https://botometer.iuni.iu.edu

```sh
autopep8 --in-place --aggressive --recursive app/bot
```

## Numpy

  + https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.normal.html
  + https://stackoverflow.com/questions/9452775/converting-numpy-dtypes-to-native-python-types/11389998

## Scipy and K-S Tests

  + https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html
  + https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html
  + https://towardsdatascience.com/when-to-use-the-kolmogorov-smirnov-test-dd0b2c8a8f61
  + https://towardsdatascience.com/kolmogorov-smirnov-test-84c92fb4158d

## Dates and Times

  + https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
  + https://docs.python.org/3/library/time.html#time.time
  + https://www.tutorialspoint.com/How-do-I-convert-a-datetime-to-a-UTC-timestamp-in-Python

## Tableau

  + [Custom Bins for Histograms of Continuous Variables](https://www.rigordatasolutions.com/post/2018/08/11/tableau-charts-histogram-graph)
  + [Filter Top N Rows per Category](https://kb.tableau.com/articles/howto/finding-the-top-n-within-a-category)
  + [Converting Timezones](https://community.tableau.com/s/question/0D54T00000C6L60/convert-utc-timezone-to-est-timezone)
  + [Completely Uninstalling](https://kb.tableau.com/articles/howto/completely-removing-tableau-desktop)

## Pandas

Grouping and aggregation, working with multi-indices:

  + https://www.kaggle.com/residentmario/grouping-and-sorting#Multi-indexes
  + https://stackoverflow.com/questions/26323926/pandas-groupby-agg-how-to-return-results-without-the-multi-index
  + https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop.html
  + https://stackoverflow.com/a/49565811/670433
  + https://stackoverflow.com/questions/22898824/filtering-pandas-dataframes-on-dates

## Matplotlib

  + https://stackoverflow.com/questions/8213522/when-to-use-cla-clf-or-close-for-clearing-a-plot-in-matplotlib#
  + https://stackoverflow.com/questions/9012487/matplotlib-pyplot-savefig-outputs-blank-image

## Plotly Express

  + https://plotly.com/python/bar-charts/#horizontal-bar-charts
  + https://plotly.com/python/orca-management/
  + https://plotly.com/python/static-image-export/

## Spacy

  + https://spacy.io/
  + https://spacy.io/models/en
  + https://spacy.io/usage/linguistic-features
  + https://spacy.io/usage/linguistic-features#native-tokenizers
  + https://spacy.io/api/token
  + https://spacy.io/api/lemmatizer
  + https://towardsdatascience.com/exploring-the-trump-twitter-archive-with-spacy-fe557810717c
  + https://towardsdatascience.com/building-a-topic-modeling-pipeline-with-spacy-and-gensim-c5dc03ffc619

## Gensim

  + https://radimrehurek.com/gensim/models/ldamulticore.html

## Regular Expressions

  + https://stackoverflow.com/questions/2527892/parsing-a-tweet-to-extract-hashtags-into-an-array

## Basilica

  + https://www.basilica.ai/available-embeddings/
  + https://basilica-client.readthedocs.io/en/latest/basilica.html?ref=://#basilica.Connection.embed_sentences

> An text embedding specialized for tweets. You can embed short snippets of text using the endpoint "api.basilica.ai/embed/text/twitter", or using `Connection.embed_sentences` with the optarg `model='twitter'` in the Python client. This embedding works best for tweets, but generalizes well to other short-form informal data like text messages.

  + https://basilica-client.readthedocs.io/en/latest/_modules/basilica.html#Connection
  + https://stackoverflow.com/a/13582705/670433

## Python Lists and Generators

  + https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks

## SKLearn

  + https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
  + https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
  + https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
  + https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html
  + https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
  + https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html
