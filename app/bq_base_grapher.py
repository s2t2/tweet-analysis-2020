
from app.base_grapher import BaseGrapher, USERS_LIMIT, BATCH_SIZE
from app.bq_service import BigQueryService

class BigQueryBaseGrapher(BaseGrapher):

    def __init__(self, users_limit=USERS_LIMIT, batch_size=BATCH_SIZE, storage_service=None, bq_service=None):
        super().__init__(users_limit=users_limit, batch_size=batch_size, storage_service=storage_service)
        self.bq_service = bq_service or BigQueryService()

    @property
    def metadata(self):
        return {**super().metadata, **{"bq_service": self.bq_service.metadata}}

if __name__ == "__main__":

    grapher = BigQueryBaseGrapher()

    grapher.start()
    grapher.perform()
    grapher.end()
    grapher.report()
