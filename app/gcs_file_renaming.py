import os
from dotenv import load_dotenv

from app import seek_confirmation
from app.gcs_service import GoogleCloudStorageService

load_dotenv()

EXISTING_DIRPATH = os.getenv("EXISTING_DIRPATH", default="storage/data/archived_graphs")
EXISTING_PATTERN = os.getenv("EXISTING_PATTERN") or EXISTING_DIRPATH # can customize pattern of files to move in the existing directory, like "storage/data/2020-", otherwise just move everything in the existing directory
NEW_DIRPATH = os.getenv("NEW_DIRPATH", default="storage/data/archived")

if __name__ == "__main__":

    #
    # RENAMING THINGS.
    # DO THIS AD-HOC, IF NECESSARY, FOR EXAMPLE IF YOU NEED TO ARCHIVE A BUNCH OF THINGS
    #

    gcs = GoogleCloudStorageService()

    blobs = list(gcs.bucket.list_blobs())

    blobs_to_rename = [blob for blob in blobs if EXISTING_PATTERN in blob.name and f"{EXISTING_PATTERN}/" != blob.name] # take all files in the dir, but not the dir itself!

    for blob in blobs_to_rename:
        print(blob)

    seek_confirmation()

    for blob in blobs_to_rename:
        #new_name = os.path.join("storage", "data", "archived_graphs", blob.name.split("storage/data")[1])
        new_name = NEW_DIRPATH + blob.name.split(EXISTING_DIRPATH)[1] # take everything after the current dirpath
        #print(new_name, "...") #> 'storage/data/archived/2020-05-25-1905/metadata.json'
        new_blob = gcs.bucket.rename_blob(blob, new_name)
        print(new_blob)
