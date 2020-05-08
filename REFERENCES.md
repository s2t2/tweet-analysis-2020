# References

## Notebook Conversion

Uploaded / imported [this notebook](/start/follower_network_collector.ipynb) [into colab](https://colab.research.google.com/drive/1T0ED71rbhiNF8HG-769aBqA0zZAJodcd), then selected "File" > "Download .py" and stored the [resulting python script](/start/follower_network_collector.py) in the "start" dir.

## Database Resources

Working with BigQuery:

  + https://cloud.google.com/bigquery/docs/reference/standard-sql/operators
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/conversion_rules
  + https://cloud.google.com/dataprep/docs/html/DATEDIF-Function_57344707
  + https://towardsdatascience.com/google-bigquery-sql-dates-and-times-cheat-sheet-805b5502c7f0
  + https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions
  + https://cloud.google.com/bigquery/docs/running-queries#batch
  + https://cloud.google.com/bigquery/docs/paging-results

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

## Network Graphs

  + https://networkx.github.io/
  + https://github.com/networkx/networkx
  + https://networkx.github.io/documentation/latest/
  + https://networkx.github.io/documentation/latest/tutorial.html
  + https://networkx.github.io/documentation/latest/reference/classes/digraph.html
  + https://networkx.github.io/documentation/latest/reference/readwrite/generated/networkx.readwrite.gpickle.read_gpickle.html
  + https://networkx.github.io/documentation/latest/reference/convert.html
  + https://networkx.github.io/documentation/latest/reference/generated/networkx.convert_matrix.from_pandas_edgelist.html

## Google Cloud Storage

  + https://dev.to/sethmlarson/python-data-streaming-to-google-cloud-storage-with-resumable-uploads-458h

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
