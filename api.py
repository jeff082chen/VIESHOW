import pymysql
db = pymysql.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    passwd='0000', 
    db='db', 
    charset='utf8'
)
  

def get_movie_info(title: str, /, db = db) -> dict:
    
    
    
    with db.cursor() as cursor:
        
        movie_info = {'movie_name': title}
        
        command = "SELECT `movie_upload_date` FROM `movie_info` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()
        movie_info ['movie_upload_date'] = result
        
        command = "SELECT `movie_director` FROM `movie_info` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()        
        movie_info ['movie_director'] = result
        
        command = "SELECT `movie_actor` FROM `movie_info` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone() 
        except:
            db.rollback()       
        movie_info ['movie_actor'] = result

        command = "SELECT `movie_type` FROM `movie_info` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()        
        movie_info ['movie_type'] = result

        command = "SELECT `movie_time` FROM `movie_info` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()
        movie_info ['movie_time'] = result
        
        command = "SELECT `movie_info` FROM `movie_info` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()
        movie_info['movie_info'] = result

        command = "SELECT `movie_version` FROM `movie` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()
        movie_info['movie_version'] = result

        command = "SELECT `movie_limit_stage` FROM `movie` WHERE `movie_name`= %s;" 
        try:
            cursor.execute(command , title)
            result = cursor.fetchone()
        except:
            db.rollback()
        movie_info['movie_stage'] = result

        cursor.close()
    return movie_info

def get_studio_info(studio_name: str, /, db = db) -> dict:
    
    with db.cursor() as cursor:
        studio_info = {'studio_name': studio_name}
        
        command = "SELECT `Cinema_address` FROM `cinema_information` WHERE `Cinema_name`= %s;" 
        try:
            cursor.execute(command , studio_name)
            result = cursor.fetchone()
        except:
            db.rollback()
        studio_info ['studio_address'] = result
        
        command = "SELECT `Cinema_tel` FROM `cinema_information` WHERE `Cinema_name`= %s;" 
        try:
            cursor.execute(command , studio_name)
            result = cursor.fetchone()
        except:
            db.rollback()
        
        studio_info ['studio_tel'] = result
        
        command = "SELECT `Cinema_intro` FROM `cinema_information` WHERE `Cinema_name`= %s;" 
        try:
            cursor.execute(command , studio_name)
            result = cursor.fetchone()
        except:
            db.rollback()
        
        studio_info ['studio_intro'] = result

        command = "SELECT `Cinema_traffic_info` FROM `cinema_information` WHERE `Cinema_name`= %s;" 
        try:
            cursor.execute(command , studio_name)
            result = cursor.fetchone()
        except:
            db.rollback()
        
        studio_info ['studio_traffic_info'] = result


        cursor.close()
    return studio_info



def get_sessions(studio_name: str , movie_title: str , date: str , time: str , /, db = db) -> list[dict]:
    
    with db.cursor() as cursor:
        sessions_info= {}
        

        command = "SELECT `movie_cinema` FROM movie  WHERE (movie_cinema = %s) AND (movie_name = %s) AND (movie_date = %s) AND (movie_time = %s) ORDER BY movie_name DESC ;" 
        try:    
            cursor.execute(command , (studio_name,movie_title,date,time))
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_cinema'] = result


        command = "SELECT `movie_name` FROM movie  WHERE (movie_cinema = %s) AND (movie_name = %s) AND (movie_date = %s) AND (movie_time = %s) ORDER BY movie_name DESC ;" 
        try:
            cursor.execute(command , (studio_name,movie_title,date,time))
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_name'] = result


        command = "SELECT `movie_date` FROM movie  WHERE (movie_cinema = %s) AND (movie_name = %s) AND (movie_date = %s) AND (movie_time = %s) ORDER BY movie_name DESC ;" 
        try:
            cursor.execute(command , (studio_name,movie_title,date,time))
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_date'] = result
        

        command = "SELECT `movie_time` FROM movie  WHERE (movie_cinema = %s) AND (movie_name = %s) AND (movie_date = %s) AND (movie_time = %s) ORDER BY movie_name DESC ;" 
        try:
            cursor.execute(command , (studio_name,movie_title,date,time))
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_time'] = result
    
        cursor.close()

    return sessions_info

# def get_empty_seats(session_id: , /, db = db) -> dict:
#     """ return empty seats remain of a session
#     parameter:
#         session id as a integer
#     return value:
#         a dictionary in a format as {'seat id': 'is_empty(bool)'}
#         or None if session not exist
#     """

#     return {}

# ... in parameter list needs to be replace as other member information

def create_new_member(account: str, password: str,mem_name:str, info_email: str, info_phone:str, info_birthday,info_creditcard_num:str, /, db = db) -> bool:
    
    with db.cursor() as cursor:
        
        try:
            command = "INSERT INTO `member`(account, password) VALUES (%s,%s);" 
            cursor.execute(command , (account,password))
            db.commit()

            command = "INSERT INTO `member_information`(`mem_name`, `info_email`, `info_phone`, `info_birthday`, `info_creditcardnum`) VALUES (%s,%s,%s,%s,%s);" 
            cursor.execute(command,(mem_name,info_email,info_phone,info_birthday,info_creditcard_num))
            db.commit()

            command = "SELECT `member_information_id` FROM `member` WHERE account = %s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            info_id = result

            command = "INSERT INTO `rec_ticket`(mem_ticket_id) VALUES (%s);"
            cursor.execute(command , info_id)
            db.commit()

        except:
           db.rollback()

        cursor.close()

    return True

def get_member_password(account: str, /, db = db) -> str:
    
    with db.cursor() as cursor:
        try:
            command = "SELECT `password` FROM `member` WHERE account =%s" 
            cursor.execute(command , account)
            result = cursor.fetchone()
        except:
           db.rollback()

        cursor.close()
    return result

def get_member_info(account: str, /, db = db) -> dict:
    
    with db.cursor() as cursor:
        mem_info ={}
        try:
            command = "SELECT `member_information_id` FROM `member` WHERE account =%s;" 
            cursor.execute(command , account)
            result = cursor.fetchone()            
            info_id = result
            
        except:
            db.rollback()
        
        try:   
            command = "SELECT `mem_name` FROM `member_information` WHERE info_id =%s;"
            cursor.execute(command , info_id)
            result = cursor.fetchone()
            mem_info['mem_name'] = result
        except:
            db.rollback()

        try:   
            command = "SELECT `info_email` FROM `member_information` WHERE info_id =%s;"
            cursor.execute(command , info_id)
            result = cursor.fetchone()
            mem_info['info_email'] = result
        except:
            db.rollback()
        
        try:   
            command = "SELECT `info_phone` FROM `member_information` WHERE info_id =%s;"
            cursor.execute(command , info_id)
            result = cursor.fetchone()
            mem_info['info_phone'] = result
        except:
            db.rollback()

        try:   
            command = "SELECT `info_birthday` FROM `member_information` WHERE info_id =%s;"
            cursor.execute(command , info_id)
            result = cursor.fetchone()
            mem_info['info_birthday'] = result
        except:
            db.rollback()  
        
        try:   
            command = "SELECT `info_point` FROM `member_information` WHERE info_id =%s;"
            cursor.execute(command , info_id)
            result = cursor.fetchone()
            if result =='NONE':
                result = 0  
            mem_info['info_point'] = result
        except:
            db.rollback()  
            
        try:   
            command = "SELECT `info_creditcardnum` FROM `member_information` WHERE info_id =%s;"
            cursor.execute(command , info_id)
            result = cursor.fetchone()
            mem_info['info_creditcardnum'] = result
        except:
            db.rollback()

        cursor.close()

    return mem_info



# def get_booking_history(account: str, /, db = db) -> list[dict]:
    
#     with db.cursor() as cursor:
#         booking_history ={}
#         try:
#             command = "SELECT `member_information_id` FROM `member` WHERE account =%s;" 
#             cursor.execute(command , account)
#             result = cursor.fetchone()            
#             info_id = result
#             booking_history ['mem_ticket_id'] = result

#             command = "SELECT `rec_movie` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec_movie'] = result

#             command = "SELECT  `rec_studio` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec_studio'] = result 
            
#             command = "SELECT  `rec_date` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec_date'] = result 
            
#             command = "SELECT  `rec_time` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec_time'] = result 
            
#             command = "SELECT  `rec_type` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec_type'] = result             
            
#             command = "SELECT  `rec_price` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec_price'] = result 

#             command = "SELECT  `popcorn` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['popcorn'] = result 

#             command = "SELECT  `drink` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['drink'] = result 

#             command = "SELECT  `rec-seat` FROM `rec_ticket` WHERE mem_ticket_id = %s"
#             cursor.execute(command , info_id)
#             result = cursor.fetchone()
#             booking_history ['rec-seat'] = result 
   
#         except:
#             db.rollback()
#     print(booking_history)

#     return booking_history

# get_booking_history('Larry')
# def seat_available(session_id: str, seat_id: int, /, db = db) -> bool:
#     """ check if a seat is available
#     parameter:
#         session id as a integer
#         seat id as a integer
#     return value:
#         a bool value indicate weather the seat is available
#     """

#     return True



def edit_member_info( mem_name:str, info_email:str, info_phone:str, info_birthday:str, info_creditcardnum: str , / , db=db): -> bool:
    
with db.cursor() as cursor:
            
            try:
                command = "UPDATE `member_information` SET `mem_name`=%s,`info_email`=%s,`info_phone`=%s,`info_birthday`=%s,`info_creditcardnum`=%s WHERE info_id = %s;" 
                cursor.execute(command , ( mem_name, info_email, info_phone, info_birthday, info_creditcardnum))
            except:
                db.rollback()

            cursor.close()
    return True

# def book_tickets():
#     return

# def edit_booking_record(booking_id: int, ..., /, db = db) -> bool:
#     return
