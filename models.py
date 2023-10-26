import random
from sqlalchemy import Column, Integer, String
from database import Base

# Function to generate random 10-digit ID
def generate_random_id():
    return random.randint(1000000000, 9999999999)  
#I have seen what I want to do , when I want to create a new database or add more fields , I will have to delete the database and add more fields to it before creating a new one 

current_id = generate_random_id()
print(current_id)


# it gets there I will set this value as a database Id value for the User database 
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, default=current_id)  # Assign the random ID when creating a new user
    name = Column(String(150))
    contact = Column(Integer)
    department_Assigned = Column(String(150))

    def __repr__(self):
        return '<User %r>' % (self.id)
#defining the second database columns