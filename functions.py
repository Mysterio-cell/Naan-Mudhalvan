import ibm_db
from os import getenv
from dotenv import load_dotenv
import ibm_boto3
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
            ibm_db.exec_immediate(self.conn, "CREATE TABLE IF NOT EXISTS complaints (id INT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY, username VARCHAR(50), email VARCHAR(50) NOT NULL, image_url VARCHAR(100), title VARCHAR(100), description VARCHAR(100), progress VARCHAR(10), status VARCHAR(10), image_after_url VARCHAR(100), FOREIGN KEY (email) REFERENCES registers(email));")
        except Exception as e:
            print(e)
        print("Connected to DB And  Created Tables")

    def check_exists(self, mail: str, password: str, type: str) -> bool:
        stmt = ibm_db.exec_immediate(
            self.conn, f"SELECT * FROM registers WHERE EMAIL = '{mail}' AND PASSWORD = '{password}' AND TYPE = '{type}'")
        return ibm_db.fetch_row(stmt)

    def check_user_exists(self, mail: str) -> bool:
        stmt = ibm_db.exec_immediate(
            self.conn, f"SELECT * FROM registers WHERE EMAIL = '{mail}'")
        return ibm_db.fetch_row(stmt)

    def add_newuser(self, name: str, mail: str, password: str, address: str, type: str) -> bool:
        try:
            print(name, mail, password, address, type)
            ibm_db.exec_immediate(
                self.conn, f"INSERT INTO registers (name, email, password, address, type) VALUES ('{name}', '{mail}', '{password}', '{address}', '{type}')")
            return True
        except Exception as e:
            print(e)
            return False

    def new_complaint(self, name: str, mail: str, subject: str, email: str) -> bool:
        try:
            ibm_db.exec_immediate(
                self.conn, f"INSERT INTO complaints (name, email, subject) VALUES ('{name}', '{email}', '{subject}', '{mail}', '{user_id}')")
            return True
        except:
            return False

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

    def upload_file(self, path: str) -> bool:
        try:
            self.cos.upload_file(
                Filename=path, Bucket=COS_BUCKET_NAME, Key=path)
            return True
        except Exception as e:
            print(e)
            return False


func = Functions()
