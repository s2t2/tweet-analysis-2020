



from app.storage_service import BigQueryService


if __name__ == "__main__":

    service = BigQueryService.cautiously_initialized()

    user_friends = service.fetch_user_friends(limit=20)
    breakpoint()
