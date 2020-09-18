
from app.bq_service import BigQueryService
#from app.retweet_graphs_v2.k_days.generator import DateRangeGenerator

if __name__ == "__main__":

    bq_service = BigQueryService()

    #gen = DateRangeGenerator()
    #for dr in gen.date_ranges:
    #    print(dr.start_date)




        # CREATE A NEW TABLE OF TWEETS ON THAT DAY

        #sql = f"""
        #"""
        #bq_service.execute_query(sql)
