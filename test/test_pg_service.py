

# test bot screen name mathing strategy, that it case-insensitively finds a given screen name in an array of screen names:

#sql = """
#   SELECT
#    'ACLU' as screen_name
#
#    ,'ACLU' ilike any('{user1, aclu}'::text[]) as t1 -- TRUE
#    ,'ACLU' ilike any('{user1, ACLU}'::text[]) as t2 -- TRUE
#    ,'ACLU' ilike any('{user1, acLu}'::text[]) as t3 -- TRUE
#
#    ,'ACLU' ilike any('{user1, user2}'::text[]) as f1 -- FALSE
#    ,'ACLU' ilike any('{user1, acluser1}'::text[]) as f2 -- FALSE
#    ,'ACLU' ilike any('{user1, aclu_ser1}'::text[]) as f3 -- FALSE
#    ,'ACLU' ilike any('{user1, aclu ser1}'::text[]) as f4 -- FALSE
#  """"
