import random
from sqlalchemy import Column, Integer, String,DateTime,ForeignKey
from database import Base
from sqlalchemy.orm import relationship

# Function to generate random 10-digit ID
def generate_random_id():
    return random.randint(1000000000, 9999999999)  

# Get the current ID value
current_id = generate_random_id()

# Define the Base class for SQLAlchemy models
class CustomBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, default=current_id)

# Define the User table
class User(CustomBase):
    __tablename__ = 'users'
    name = Column(String(150))
    contact = Column(Integer)
    department_Assigned = Column(String(150))



     # Establish a relationship with the Attendance table
    attendances = relationship("Attendance", back_populates="user")
    def __repr__(self):
        return '<User %r>' % (self.id)

# Define the Attendance table
class Attendance(CustomBase):
    __tablename__ = "attendance"
    # Add other columns for day, date, and time
    user_id=Column(Integer,ForeignKey('users.id'))
    sign_in_time = Column(DateTime, nullable=True)  # Timestamp for sign-in (mandatory)
    sign_out_time = Column(DateTime, nullable=True)   # Timestamp for sign-out (nullable)
    sign_in_date = Column(String(50), nullable=True)  
    sign_out_date = Column(String(50), nullable=True)


    # Establish a back-reference to the User table
    user = relationship("User", back_populates="attendances")

    def __repr__(self):
        return '<Attendance %r>' % (self.user_id)
