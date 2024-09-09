# import psycopg2
# from psycopg2.extras import RealDictCursor
#
# # conn = psycopg2.connect(host='localhost', port= '5433', user='postgres', password='1234')
# # cur = conn.cursor()
# # conn.set_session(autocommit = True)
#
#
# # connect to database
# def get_connection():
#     conn = psycopg2.connect(
#         host = 'localhost',
#         port = '5433',
#         user = 'postgres',
#         password = '1234',
#         database = 'todoapp'
#     )
#     conn.set_session(autocommit = True)
#     return conn
#
# # get cursor
# def get_cursor(): # cursor nhu mot con tro tro vao vi tri cua db
#     conn = get_connection()
#     return conn.cursor(cursor_factory = RealDictCursor) # nhan ket qua duoi dang tu dien luon do phai xu li
