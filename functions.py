import ibm_db
from os import getenv
from dotenv import load_dotenv
import ibm_boto3
import string
import random
from constants import *
from ibm_botocore.client import Config

load_dotenv()

DB_URL = getenv("DB_URL")


class Functions:
    def __init__(self):
        self.conn = ibm_db.connect(
            DB_URL, '', '')
        self.create_tables()
        self.cos = self.setup_s3()

    def create_tables(self):
        try:
            ibm_db.exec_immediate(
                self.conn, "CREATE TABLE IF NOT EXISTS registers (id INT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY, name VARCHAR(50), email VARCHAR(50) NOT NULL UNIQUE, password VARCHAR(20), role VARCHAR(10));")
            ibm_db.exec_immediate(self.conn, "CREATE TABLE IF NOT EXISTS complaints (id INT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY, username VARCHAR(50), email VARCHAR(50) NOT NULL, image_url VARCHAR(100), title VARCHAR(100), description VARCHAR(100), location_details VARCHAR(100), latitute VARCHAR(20), longitute VARCHAR(20), FOREIGN KEY (email) REFERENCES registers(email));")
            ibm_db.exec_immediate(self.conn, "CREATE TABLE IF NOT EXISTS tasks (id INT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY, username VARCHAR(50), email VARCHAR(50) NOT NULL, image_url VARCHAR(100), title VARCHAR(100), description VARCHAR(100), progress VARCHAR(10), status VARCHAR(10), image_after_url VARCHAR(100), agent_id VARCHAR(10), updated_status VARCHAR(100), FOREIGN KEY (email) REFERENCES registers(email));")
        except Exception as e:
            print(e)
        print("Connected to DB And  Created Tables")

    def check_exists(self, mail: str, password: str, type: str) -> bool:
        stmt = ibm_db.exec_immediate(
            self.conn, f"SELECT * FROM registers WHERE EMAIL = '{mail}' AND PASSWORD = '{password}' AND ROLE = '{type}'")
        return ibm_db.fetch_row(stmt)

    def check_user_exists(self, mail: str) -> bool:
        stmt = ibm_db.exec_immediate(
            self.conn, f"SELECT * FROM registers WHERE EMAIL = '{mail}'")
        return ibm_db.fetch_row(stmt)

    def add_newuser(self, name: str, mail: str, password: str, type: str) -> bool:
        try:
            ibm_db.exec_immediate(
                self.conn, f"INSERT INTO registers (name, email, password, role) VALUES ('{name}', '{mail}', '{password}', '{type}')")
            return True
        except Exception as e:
            print(e)
            return False

    def new_complaint(self, title: str, description: str, mail: str, image_url: str, latitute: str, longitute: str, location_details: str) -> bool:
        try:
            query = "INSERT INTO complaints (username, email, image_url, title, description, location_details, LATITUTE, LONGITUTE) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
            query = query.format(mail.split('@')[0], mail, image_url, title, description,location_details , latitute, longitute)

            ibm_db.exec_immediate(self.conn, query)
            return True
        except Exception as e:
            print(e)
            return False
        

    def get_complaint(self):
        try:
            query = "SELECT * FROM complaints"
            stmt = ibm_db.exec_immediate(self.conn, query)
            result = ibm_db.fetch_assoc(stmt)
    

            complaints = []
            while result:
                complaint = {
                    'id': result['ID'],
                    'username': result['USERNAME'],
                    'email': result['EMAIL'],
                    'image_url': result['IMAGE_URL'],
                    'title': result['TITLE'],
                    'description': result['DESCRIPTION'],
                    'location_details': result['LOCATION_DETAILS'],
                    'latitude': result['LATITUTE'],
                    'longitude': result['LONGITUTE']
                }
                complaints.append(complaint)
                result = ibm_db.fetch_assoc(stmt)
           
            return complaints
        except Exception as e:
            print(e,"is the error")
            return []


    def get_complaints(self) -> list:
        stmt = ibm_db.exec_immediate(self.conn, "SELECT * FROM complaints")
        return ibm_db.fetch_assoc(stmt)

    def setup_s3(self):
        try:
            cos = ibm_boto3.client(service_name='s3',
                                   ibm_api_key_id=COS_API_KEY_ID,
                                   ibm_service_instance_id=COS_RESOURCE_CRN,
                                   config=Config(signature_version='oauth'),
                                   endpoint_url=COS_ENDPOINT)
            return cos
        except Exception as e:
            print(e)
            return None

    def upload_file(self, path: str) -> str:
        try:
            self.cos.upload_file(
                Filename=path, Bucket=COS_BUCKET_NAME, Key=path)
            return f"{COS_ENDPOINT}{COS_BUCKET_NAME}/{path}"
        except Exception as e:
            print(e)
            return None

    def generate_random_string(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(10)) + '.jpg'


func = Functions()
