from pickleball_app.config.mysqlconnection import connectToMySQL
from pickleball_app.models.user_model import User
from pprint import pprint

db = "pickleball_db"

class Event:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.date = data['date']
        self.streetNumber = data['streetNumber']
        self.streetName = data['streetName']
        self.municipality = data['municipality']
        self.countrySubdivision = data['countrySubdivision']
        self.postalCode = data['postalCode']
        self.capacity = data['capacity']
        self.information = data['information']
        self.url = data['url']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.creator = None
        self.going = []

    # Display all Events
    @classmethod
    def all_events(cls):
        query = "SELECT * FROM events"
        results = connectToMySQL(db).query_db(query)
        events = []
        for event in results:
            events.append(cls(event))
        return events

    # Create New Event
    @classmethod
    def create_event(cls, data):
        query = """
                INSERT INTO events ( title, date, streetNumber, streetName, municipality, countrySubdivision, postalCode, capacity, information, url, user_id )
                VALUES ( %(title)s, %(date)s, %(streetNumber)s, %(streetName)s, %(municipality)s, %(countrySubdivision)s, %(postalCode)s, %(capacity)s, %(information)s, %(url)s, %(user_id)s );
                """
        return connectToMySQL(db).query_db(query, data)

    # Update Event
    @classmethod
    def update_event(cls, data, event_id):
        query = f"UPDATE events SET title = %(title)s, date = %(date)s, streetNumber = %(streetNumber)s, streetName = %(streetName)s, municipality = %(municipality)s, countrySubdivision = %(countrySubdivision)s, postalCode = %(postalCode)s, capacity = %(capacity)s, information = %(information)s, url = %(url)s WHERE id = {event_id}"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def show_one_event(cls, data):
        query = """
                SELECT * FROM events
                LEFT JOIN users on users.id = events.user_id
                WHERE events.id = %(id)s
                """
        results = connectToMySQL(db).query_db(query, data)
        print(results)
        event = cls(results[0])
        user_data = {
            'id' : results[0]['users.id'],
            'first_name' : results[0]['first_name'],
            'last_name' : results[0]['last_name'],
            'email' : results[0]['email'],
            'password' : results[0]['password'],
            'created_at' : results[0]['created_at'],
            'updated_at' : results[0]['updated_at'],
        }
        event.creator = User(user_data)
        return event

    @classmethod
    def join_event(cls, data):
        query = """
                INSERT INTO attendance ( user_id, event_id )
                VALUES ( %(user_id)s, %(event_id)s )
                """
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def unjoin_event(cls, data):
        query = """
                DELETE FROM attendance
                WHERE event_id = %(event_id)s
                AND user_id = %(user_id)s
                """
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def users_who_created_events(cls):
        query = """
                SELECT * FROM events
                JOIN users ON events.user_id = users.id
                """
        results = connectToMySQL(db).query_db(query)
        events = []
        for event in results:
            event_creator = cls(event)
            user_data = {
                'id' : event['id'],
                'first_name' : event['first_name'],
                'last_name' : event['last_name'],
                'email' : event['email'],
                'password' : event['password'],
                'created_at' : event['created_at'],
                'updated_at' : event['updated_at'],
            }
            event_creator = User(user_data)
            events.append(event_creator)
        return events

    @classmethod
    def users_who_are_attending(cls, data):
        query = """
                SELECT * FROM events
                JOIN users ON users.id = events.user_id
                LEFT JOIN attendance ON events.id = attendance.event_id
                LEFT JOIN users AS users2 ON users2.id = attendance.user_id;
                """
        results = connectToMySQL(db).query_db(query, data)
        pprint(results, sort_dicts=False, width=1)
        attendance = []
        for result in results:
            now_attending = True
            attending_user_data = {
                'id' : result['users2.id'],
                'first_name' : result['users2.first_name'],
                'last_name' : result['users2.last_name'],
                'email' : result['users2.email'],
                'password' : result['users2.password'],
                'created_at' : result['users2.created_at'],
                'updated_at' : result['users2.updated_at'],
            }
            if len(attendance) > 0 and attendance[len(attendance)-1].id == result['id']:
                attendance[len(attendance)-1].going.append(User(attending_user_data))
                now_attending = False
            if now_attending:
                attending = cls(result)
                user_data = {
                    'id' : result['users.id'],
                    'first_name' : result['first_name'],
                    'last_name' : result['last_name'],
                    'email' : result['email'],
                    'password' : result['password'],
                    'created_at' : result['users.created_at'],
                    'updated_at' : result['users.updated_at']
                    }
                user = User(user_data)
                attending.user = user
                if result['users2.id'] is not None:
                    attending.going.append(User(attending_user_data))
                attendance.append(attending)
        return attendance

    @classmethod
    def delete_event(cls, data):
        query = """
                DELETE FROM events
                WHERE id = %(id)s;
                """
        return connectToMySQL(db).query_db(query, data)