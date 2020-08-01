
#import psycopg2
#
#from app.base_grapher import BaseGrapher, DRY_RUN, BATCH_SIZE, USERS_LIMIT
#from app.models import DATABASE_URL, USER_FRIENDS_TABLE_NAME
#
#class PsycopgBaseGrapher(BaseGrapher):
#    def __init__(self, dry_run=DRY_RUN, batch_size=BATCH_SIZE, users_limit=USERS_LIMIT,
#                        database_url=DATABASE_URL, table_name=USER_FRIENDS_TABLE_NAME):
#        super().__init__(dry_run=dry_run, batch_size=batch_size, users_limit=users_limit)
#        self.database_url = database_url
#        self.table_name = table_name
#        self.connection = psycopg2.connect(self.database_url)
#        self.cursor = self.connection.cursor(name="network_grapher", cursor_factory=psycopg2.extras.DictCursor) # A NAMED CURSOR PREVENTS MEMORY ISSUES!!!!
#
#    @property
#    def metadata(self):
#        return {**super().metadata, **{"database_url": self.database_url, "table_name": self.table_name}} # merges dicts
#
