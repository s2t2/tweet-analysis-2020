



def fetch_in_batches():
    print("MOCK: `pg_service.get_something(limit=LIMIT)`")
    while True:
        print("MOCK: `batch = pg_service.cursor.fetchmany(size=BATCH_SIZE)`")
        if batch:
            yield batch
        else:
            break
    print("MOCK: `pg_service.close()`")
    print("COMPLETE!")

def perform():
    counter = 0
    for batch in fetch_in_batches():
        counter += len(batch)
        print(logstamp(), fmt_n(counter))


if __name__ == "__main__":

    perform()
