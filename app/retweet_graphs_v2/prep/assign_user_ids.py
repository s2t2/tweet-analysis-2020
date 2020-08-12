from pprint import pprint

from app import seek_confirmation # DATA_DIR
from app.decorators.datetime_decorators import logstamp
from app.decorators.number_decorators import fmt_n
from app.bq_service import BigQueryService

if __name__ == "__main__":

    bq_service = BigQueryService()

    print("-------------------------")
    screen_names = [row.screen_name for row in bq_service.fetch_idless_screen_names_postlookup()]
    print("FETCHED", fmt_n(len(screen_names)), "SCREEN NAMES...") # 2,224

    max_user_id = bq_service.fetch_max_user_id_postlookup()
    print("-------------------------")
    print("MAX ID:")
    print(max_user_id)

    print("-------------------------")
    print("ASSIGNING IDS...")
    assignments = []
    for screen_name in screen_names:
        max_user_id+=1
        assignments.append({"screen_name": screen_name, "user_id": max_user_id})
    #pprint(assignments)

    print(assignments[0]["user_id"])
    print("...")
    print(assignments[-1]["user_id"])
    print("-------------------------")

    seek_confirmation()
    bq_service.migrate_user_id_assignments_table()
    bq_service.upload_user_id_assignments(assignments)
    print("UPLOAD COMPLETE!")
