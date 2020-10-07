# Don't use this method. Just fetch tweets once otherwise its very expensive

#import os
#
#from app import seek_confirmation
#from app.job import Job
#from app.bq_service import BigQueryService
#from app.nlp.model_storage import ModelStorage
#
#LIMIT = os.getenv("LIMIT")
#BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100000"))
#
#if __name__ == "__main__":
#
#    for model_name in ["logistic_regression", "multinomial_nb"]:
#
#        storage = ModelStorage(dirpath=f"nlp_v2/models/best/{model_name}")
#        tv = storage.load_vectorizer()
#        clf = storage.load_model()
#
#        bq_service = BigQueryService()
#
#        print(f"DESTROY PREDICTIONS TABLE? ({model_name})")
#        seek_confirmation()
#        bq_service.nlp_v2_destructively_migrate_predictions_table(model_name)
#        predictions_table = bq_service.nlp_v2_get_predictions_table(model_name) # API call. cache it here once.
#
#        job = Job()
#        job.start()
#
#        ids_batch = []
#        statuses_batch = []
#        for row in bq_service.nlp_v2_fetch_statuses(limit=LIMIT):
#            ids_batch.append(row["status_id"])
#            statuses_batch.append(row["status_text"])
#
#            job.counter += 1
#            if job.counter % BATCH_SIZE == 0:
#                preds = clf.predict(tv.transform(statuses_batch))
#                batch = [{"status_id": s_id, "prediction": pred} for s_id, pred in zip(ids_batch, preds)]
#                bq_service.insert_records_in_batches(predictions_table, batch)
#
#                job.progress_report()
#                ids_batch = []
#                statuses_batch = []
#                batch = []
#
#        if len(statuses_batch) > 0:
#            preds = clf.predict(tv.transform(statuses_batch))
#            batch = [{"status_id": s_id, "prediction": pred} for s_id, pred in zip(ids_batch, preds)]
#            bq_service.insert_records_in_batches(predictions_table, batch)
#
#            job.progress_report()
#            ids_batch = []
#            statuses_batch = []
#            batch = []
#
#        job.end()
#
