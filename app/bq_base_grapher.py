
from app.base_grapher import BaseGrapher
from app.bq_service import BigQueryService

class BigQueryBaseGrapher(BaseGrapher):

    def __init__(self, bq_service=None):
        super().__init__()
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
