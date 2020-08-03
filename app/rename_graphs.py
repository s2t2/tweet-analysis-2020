




import os

from app import seek_confirmation
from app.gcs_service import GoogleCloudStorageService


if __name__ == "__main__":

    gcs = GoogleCloudStorageService()

    blobs = list(gcs.bucket.list_blobs())

    blobs_to_rename = [blob for blob in blobs if "storage/data/2020-" in blob.name]

    for blob in blobs_to_rename:
        print(blob)

    seek_confirmation()

    for blob in blobs_to_rename:
        #new_name = os.path.join("storage", "data", "archived_graphs", blob.name.split("storage/data")[1])
        new_name = "storage/data/archived_graphs" + blob.name.split("storage/data")[1]
        #> 'storage/data/archived_graphs/2020-05-25-1905/metadata.json'
        print(new_name, "...")
        new_blob = gcs.bucket.rename_blob(blob, new_name)
