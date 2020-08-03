
from app.base_grapher import BaseGrapher, USERS_LIMIT, BATCH_SIZE
from app.bq_service import BigQueryService

class BigQueryBaseGrapher(BaseGrapher):

    def __init__(self, job_id=None, storage_service=None, users_limit=USERS_LIMIT, batch_size=BATCH_SIZE, bq_service=None):
        super().__init__(job_id=job_id, storage_service=storage_service, users_limit=users_limit, batch_size=batch_size)
        self.bq_service = bq_service or BigQueryService()

    @property
    def metadata(self):
        return {**super().metadata, **self.bq_service.metadata} # merges dicts

if __name__ == "__main__":

    grapher = BigQueryBaseGrapher()

    # print(type(grapher))
    # print(type(grapher.bq_service))
    # print(type(grapher.gcs_service))
    # print(dir(grapher))

    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
