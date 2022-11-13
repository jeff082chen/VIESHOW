
import pymysql

db = pymysql.connect(
    host = '', 
    port = , 
    user = '', 
    passwd = '', 
    db = ''
)



def get_movie_info(title: str, /, db = db) -> dict:
    """ return all information of a movie

    parameter:
        movie title as a string

    return value:
        a dictionary structure with movie information
        or None if movie not exist
    """

    return {}

def get_studio_info(studio_name: str, /, db = db) -> dict:
    """ return all information of a studio

    parameter:
        studio name as a string

    return value:
        a dictionary structure with studio information
        or None if studio not exist
    """

    return {}

def get_sessions(studio_name: str = None, movie_title: str = None, date: datetime.date = None, time: datetime.time = None, /, db = db) -> list[dict]:
    """ return all movie sessions that match given condition

    parameter: (None if not specify)
        studio name as a string
        movie title as a string
        date as datetime.date
        time as datetime.time

    return value:
        a list of dictionary with all session information
        empty list if there's no sessions match given condition
    """

    return []

def get_empty_seats(session_id: int, /, db = db) -> dict:
    """ return empty seats remain of a session

    parameter:
        session id as a integer

    return value:
        a dictionary in a format as {'seat id': 'is_empty(bool)'}
        or None if session not exist
    """

    return {}

# ... in parameter list needs to be replace as other member information
def creat_new_member(account: str, password: str, ..., /, db = db) -> bool:
    """ creat a new member account

    parameter:
        member informations

    return value:
        a bool value indicate weather the operation is succeed
    """

    return True

def get_member_password(account: str, /, db = db) -> str:
    """ get member's password with account

    parameter:
        member account as string

    return value:
        password as string
        or None if member not exist
    """

    return "0000"

def get_member_info(account: str, /, db = db) -> dict:
    """ get member's infomation with account

    parameter:
        member account as string

    return value:
        all member info as a dictionary
        or None if member not exist
    """

    return {}

def get_booking_history(account: str, /, db = db) -> list[dict]:
    """ get all booking histories of a member

    parameter:
        member account as string

    return value:
        a list of dictionary contain all booking informations
        or None if member not exist, empty list if no history exist
    """

    return []

def seat_available(session_id: str, seat_id: int, /, db = db) -> bool:
    """ check if a seat is available

    parameter:
        session id as a integer
        seat id as a integer

    return value:
        a bool value indicate weather the seat is available
    """

    return True



def edit_member_info():
    return

def book_tickets():
    return

def edit_booking_record(booking_id: int, ..., /, db = db) -> bool:
    return