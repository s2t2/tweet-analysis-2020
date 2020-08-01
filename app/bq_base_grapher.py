
from app.base_grapher import BaseGrapher
from app.bq_service import BigQueryService

class BigQueryBaseGrapher(BaseGrapher):

    def __init__(self, bq_service=None, gcs_service=None):
        super().__init__(gcs_service=gcs_service)
        self.bq_service = (bq_service or BigQueryService.cautiously_initialized())

    @property
    def metadata(self):
        return {**super().metadata, **self.bq_service.metadata} # merges dicts
