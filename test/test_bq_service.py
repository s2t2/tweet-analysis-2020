
import pytest

from conftest import CI_ENV
from app.bq_service import BigQueryService, split_into_batches


def test_split_into_batches():
    batches = split_into_batches([0,1,2,3,4,5,6,7,8,9,10], 3)
    assert list(batches) == [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [9, 10]
    ]

@pytest.mark.skipif(CI_ENV, reason="avoid issuing HTTP requests on CI")
def test_upload_in_batches():

    bq_service = BigQueryService(dataset_name="impeachment_test")

    # when inserting more than 10,000 rows,
    # is able to overcome error "too many rows present in the request, limit: 10000":
    lots_of_rows = [{"start_date":"2020-01-01", "user_id":i, "bot_probability": .99} for i in range(1, 36000)]
    errors = bq_service.upload_daily_bot_probabilities(lots_of_rows)
    assert not any(errors)
