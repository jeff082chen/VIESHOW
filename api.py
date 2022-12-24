import pymysql

db = pymysql.connect(
    host='localhost', 
    port=3306, 
    user='jeffrey', 
    passwd='', 
    db='VIESHOW'
)

def get_all_movies(db = db):
    with db.cursor() as cursor:
        command = "SELECT `movie_name` FROM `movie_info` WHERE 1;"
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
    return result

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

def get_all_studios(db = db):
    with db.cursor() as cursor:
        command = "SELECT `Cinema_name`, `Cinema_address`, `Cinema_tel` FROM `cinema_information` WHERE 1;"
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
    return result

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

def get_sessions(studio_name = None, movie_title = None, date = None, time = None, db = db) -> list[dict]:

    with db.cursor() as cursor:
        sessions_info= {}
        command= "SELECT `movie_cinema` FROM movie WHERE 1 "
        if studio_name is not None:
            command += f'AND movie_cinema = "{studio_name}" '
        if movie_title is not None:
            command += f'AND movie_name = "{movie_title}" '
        if date is not None:
            command += f'AND movie_date = "{date}" '
        if time is not None:
            command += f'AND movie_time = "{time}" '
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_cinema'] = result


        command= "SELECT `movie_name`, `movie_limit_stage` FROM movie WHERE 1 "
        if studio_name is not None:
            command += f'AND movie_cinema = "{studio_name}" '
        if movie_title is not None:
            command += f'AND movie_name = "{movie_title}" '
        if date is not None:
            command += f'AND movie_date = "{date}" '
        if time is not None:
            command += f'AND movie_time = "{time}" '
        try:     
            cursor.execute(command )
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_info'] = result


        command= "SELECT `movie_date` FROM movie WHERE 1 "
        if studio_name is not None:
            command += f'AND movie_cinema = "{studio_name}" '
        if movie_title is not None:
            command += f'AND movie_name = "{movie_title}" '
        if date is not None:
            command += f'AND movie_date = "{date}" '
        if time is not None:
            command += f'AND movie_time = "{time}" '
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_date'] = result
        

        command= "SELECT `movie_time` FROM movie WHERE 1 "
        if studio_name is not None:
            command += f'AND movie_cinema = "{studio_name}" '
        if movie_title is not None:
            command += f'AND movie_name = "{movie_title}" '
        if date is not None:
            command += f'AND movie_date = "{date}" '
        if time is not None:
            command += f'AND movie_time = "{time}" '
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_time'] = result

        command= "SELECT `movie_version` FROM movie WHERE 1 "
        if studio_name is not None:
            command += f'AND movie_cinema = "{studio_name}" '
        if movie_title is not None:
            command += f'AND movie_name = "{movie_title}" '
        if date is not None:
            command += f'AND movie_date = "{date}" '
        if time is not None:
            command += f'AND movie_time = "{time}" '
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
        sessions_info['movie_version'] = result
    
        cursor.close()

    return sessions_info

def create_new_member(account: str, password: str,mem_name:str, mem_email: str, mem_phone:str, mem_birthday,mem_creditcard_num:str,mem_veri: str, /, db = db) -> bool:
    
    with db.cursor() as cursor:
        
        try:
            command = f'INSERT INTO `member` (`account`, `password`, `mem_name`, `mem_email`, `mem_phone`, `mem_birthday`, `mem_point`, `mem_creditcardnum`, `mem_veri`, `veri_pass`) VALUES ("{account}","{password}","{mem_name}","{mem_email}","{mem_phone}","{mem_birthday}","0","{mem_creditcard_num}","{mem_veri}","0");'
            cursor.execute(command)
            db.commit()
        except:
            db.rollback()
            return False

        cursor.close()

    return True

def member_is_valid(account: str, /, db = db) -> bool:

    with db.cursor() as cursor:
        try:
            command = f'SELECT `veri_pass` FROM member WHERE account = "{account}"'
            cursor.execute(command)
            result = cursor.fetchone()
        except:
           db.rollback()

        cursor.close()
    return result

def verify_member(account: str, /, db = db):

    with db.cursor() as cursor:
        try:
            command = f'UPDATE member SET `veri_pass` = 1 WHERE account = "{account}"'
            cursor.execute(command)
            db.commit()
        except:
           db.rollback()

        cursor.close()

def get_member_password(account: str, /, db = db) -> str:
    
    with db.cursor() as cursor:
        try:
            command = f"SELECT `password` FROM `member` WHERE account ='{account}'" 
            cursor.execute(command)
            result = cursor.fetchone()
        except:
           db.rollback()

        cursor.close()
    return result

def get_member_verification_code(account: str, /, db = db) -> str:
    
    with db.cursor() as cursor:
        try:
            command = f"SELECT `mem_veri` FROM `member` WHERE account ='{account}'" 
            cursor.execute(command)
            result = cursor.fetchone()
        except:
           db.rollback()

        cursor.close()
    return result

def get_member_info(account: str, /, db = db) -> dict:
    
    with db.cursor() as cursor:
        mem_info ={}        
        try:   
            command = "SELECT `mem_name` FROM `member_information` WHERE account =%s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            mem_info['mem_name'] = result
        except:
            db.rollback()

        try:   
            command = "SELECT `mem_email` FROM `member_information` WHERE account =%s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            mem_info['mem_email'] = result
        except:
            db.rollback()
        
        try:   
            command = "SELECT `mem_phone` FROM `member` WHERE account =%s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            mem_info['mem_phone'] = result
        except:
            db.rollback()

        try:   
            command = "SELECT `mem_birthday` FROM `member_information` WHERE account =%s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            mem_info['mem_birthday'] = result
        except:
            db.rollback()  
        
        try:   
            command = "SELECT `mem_point` FROM `member_information` WHERE account =%s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            if result =='NONE':
                result = 0  
            mem_info['mem_point'] = result
        except:
            db.rollback()  
            
        try:   
            command = "SELECT `mem_creditcardnum` FROM `member_information` WHERE account =%s;"
            cursor.execute(command , account)
            result = cursor.fetchone()
            mem_info['mem_creditcardnum'] = result
        except:
            db.rollback()

        cursor.close()

    return mem_info

def edit_member_info( account: str,mem_name:str, mem_email:str, mem_phone:str, mem_birthday:str, mem_creditcardnum: str , / , db=db) -> bool:
    
    with db.cursor() as cursor:
            
            command= "UPDATE `member` SET "
            if mem_name is not None:
                command += " `mem_name`= '{mem_name}' "
            if mem_email is not None:
                command += " `mem_eamil` = '{mem_email}' "
            if mem_phone is not None:
                command += " `mem_phone` = '{mem_phone}' "
            if mem_birthday is not None:
                command += " `mem_creditcardnum` = '{mem_creditcardnum}' "          
            command += "WHERE 'account' = '{account};'"
            try:    
                cursor.execute(command)
                db.commit()
            except:
                db.rollback()

            cursor.close()
    
    return True

def get_empty_seats(session_id: int , / , db = db) -> dict:
    """ return empty seats remain of a session
    parameter:
    session id as a integer
    return value:
    a dictionary in a format as {'seat id': 'is_empty(bool)'}
    or None if session not exist
    """
    with db.cursor() as cursor:
        try:
            command = "SELECT `seat` FROM `seat` WHERE `movie_ses` = %s AND seat_bool = 0;" 
            cursor.execute(command,session_id)
            result = cursor.fetchall()
        except:
           db.rollback()

        cursor.close()

    return result


def get_booking_history(account: str, /, db = db) -> list[dict]:
    
    with db.cursor() as cursor:
        booking_history ={}
        
        try:
            command = "SELECT `rec_movie` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['rec_movie'] = result
        except:
            db.rollback()
        
        try:
            command = "SELECT `rec_studio` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['rec_studio'] = result
        except:
            db.rollback()
        
        try:
            command = "SELECT `rec_date` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['rec_date'] = result
        except:
            db.rollback()

        try:
            command = "SELECT `rec_time` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['rec_time'] = result
        except:
            db.rollback()
        
        try:
            command = "SELECT `ticket_type` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['ticket_type'] = result
        except:
            db.rollback()

        try:
            command = "SELECT `ticket_price` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['ticket_price'] = result
        except:
            db.rollback()
        
        try:
            command = "SELECT `drink` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['drink'] = result
        except:
            db.rollback()
        
        try:
            command = "SELECT `popcorn` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['popcorn'] = result
        except:
            db.rollback()
        
        try:
            command = "SELECT `rec_seat` FROM `rec_ticket` WHERE account = %s"
            cursor.execute(command,account)
            result = cursor.fetchall()
            booking_history ['rec_seat'] = result
        except:
            db.rollback()
            
    return booking_history


def book_tickets(account:str,rec_movie:str,rec_studio:str,rec_date:str,rec_time:str,ticket_type:str ,popcorn:str ,drink:str, rec_seat:str , / ,db=db):
    
    with db.cursor() as cursor:
        command = "INSERT INTO `rec_ticket`(`account`, `rec_movie`, `rec_studio`, `rec_date`, `rec_time`, `ticket_type`, `type_price`, `rec-seat`, `popcorn`, `drink`) VALUES('{account}','{rec_movie}','{rec_studio}'.'{rec_date}','{rec_time}','{ticket_type}','{type_price}', '{rec_seat}'"
        if popcorn is not None:
            command += ",'{popcorn}'"
        if drink is not None:
            command += ",'{drink}'"
        command +=");"
        cursor.execute(command)
        db.commit()

        command = "SELECT `movie_ses` FROM `movie` WHERE 'movie_name' = '{rec_movie}' AND 'movie_cinema' = '{rec_studio}' AND 'movie_date' = '{rec_date}', AND 'movie_time' ='{movie_time}'; "
        cursor.execute(command,())
        ses_id = cursor.fetchone()
        command = "UPDATE `seat` SET `seat_bool`='1' WHERE `movie_ses`=%s AND`seat` = %s "
        try:    
            cursor.execute(command,(ses_id,rec_seat))
            db.commit()
        except:
            db.rollback()

        cursor.close()
    
    return True

def seat_available(session_id: int, seat_id: str, /, db = db) -> bool:
    
    with db.cursor() as cursor:
        try:
            command = "SELECT `seat_bool` FROM `seat` WHERE `movie_ses` = %s AND 'seat' = %s;" 
            cursor.execute(command,(session_id,seat_id))
            result = cursor.fetchone()
            if result is not None:
                return False
        except:
           db.rollback()

        cursor.close()

    return True

def edit_booking_record(ticket_id: int, rec_movie:str,rec_studio:str,rec_date:str,rec_time:str,ticket_type:str,type_price:int,popcorn:str,drink:str,rec_seat:str, /, db = db) -> bool:
    
    with db.cursor() as cursor:
        command= "UPDATE `rec_ticket` SET "
        if rec_movie is not None:
            command += " `rec_movie`= '{rec_movie}' "
        if rec_studio is not None:
            command += " `rec_studio` = '{rec_studio}' "
        if rec_date is not None:
            command += " `rec_date` = '{rec_date}' "
        if rec_time is not None:
            command += " `rec_time` = '{rec_time}' "    
        if ticket_type is not None:
            command += " `ticket_type` = '{ticket_type}' "  
        if type_price is not None:
            command += " `type_price` = '{type_price}' "  
        if popcorn is not None:
            command += " `popcorn` = '{popcorn}' " 
        if drink is not None:
            command += " `drink` = '{drink}' " 
        if rec_seat is not None:
            command += " `rec_seat` = '{rec_seat}' "     
        command += "WHERE 'ticket_id' = '{ticket_id};'"
        cursor.execute(command)
        db.commit()
        
        cursor.close()
    return True
