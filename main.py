#crud/main.py
from fastapi import FastAPI, Request, Depends, Form, status,HTTPException
from fastapi.templating import Jinja2Templates
import models
from datetime import datetime
from database import engine, sessionlocal
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import date,time 
 
models.Base.metadata.create_all(bind=engine)
 
templates = Jinja2Templates(directory="templates")
 
app = FastAPI()
 
app.mount("/static", StaticFiles(directory="static"), name="static")
 
def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
 
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.desc())
    return templates.TemplateResponse("index.html", {"request": request, "users": users})
 
@app.post("/add")
async def add(request: Request, name: str = Form(...), contact: str = Form(...), department: str = Form(...), db: Session = Depends(get_db)):
    print(name)
    print(contact)
    print(department)
    users = models.User(name=name, contact=contact, department_Assigned=department)
    db.add(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
 
@app.get("/addnew")
async def addnew(request: Request):
    return templates.TemplateResponse("addnew.html", {"request": request})
 
@app.get("/edit/{user_id}")
async def edit(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "user": user})
 
@app.post("/update/{user_id}")
async def update(request: Request, user_id: int, name: str = Form(...), contact: str = Form(...), department: str = Form(...), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.id == user_id).first()
    users.name = name
    users.contact = contact
    users.department_Assigned = department
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
 
@app.get("/delete/{user_id}")
async def delete(request: Request, user_id: int, db: Session = Depends(get_db)):
    # Retrieve the user
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Check if the user exists
    if user:
        # Retrieve and delete associated attendance records
        attendances = db.query(models.Attendance).filter(models.Attendance.user_id == user_id).all()
        for attendance in attendances:
            db.delete(attendance)
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        # Redirect to the home page after deletion
        return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
    else:
        # User not found, raise an error
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found in the database.")






## working on the routing for the interns views , the first one is the checkin route 
@app.get("/checkin")
async def checkin(request:Request):
    return templates.TemplateResponse("Attendance Ui/index.html",{"request":request})

#checkout view 
@app.get("/checkout")
async def checkout(request:Request):
    return templates.TemplateResponse("Attendance Ui/signup.html",{"request":request})





@app.post("/checkin")
async def checkin(request: Request, id_number: int = Form(...), db: Session = Depends(get_db)):
    print(id_number)

    # Get the current date and time
    sign_time = datetime.now()
    sign_date = sign_time.strftime("%Y-%m-%d %H:%M:%S")  # Format the date and time as needed
    today_date = date.today().strftime("%Y-%m-%d")  # Get today's date in the same format

    # Check if the user ID exists in the database
    user = db.query(models.User).filter(models.User.id == id_number).first()

    if user:
        # Check if the user has already signed in today
        existing_attendance = db.query(models.Attendance).filter(
            models.Attendance.user_id == id_number,
            models.Attendance.sign_in_date == today_date
        ).first()

        if existing_attendance:
            print("User has already signed in today.")
            message = "You have already signed in today: {}".format(id_number)
        else:
            # User exists and has not signed in today, create attendance record
            attendance = models.Attendance(user_id=id_number, sign_in_time=sign_time, sign_in_date=today_date)
            db.add(attendance)
            db.commit()
            print("The user is in the database and it has been successfully added")
            message = "You have signed in successfully: {}".format(id_number)
    else:
        # User does not exist, raise an HTTPException with 404 status code
        print("There is an error, user is not in our database")
        message = "Error: User ID {} not found in the database.".format(id_number)
        raise HTTPException(status_code=404, detail=message)

    # Pass the message to the template response
    return templates.TemplateResponse("Attendance Ui/index.html", {"request": request, "message": message})


        



@app.post("/checkout")
async def checkout(request: Request, id_number: int = Form(...), db: Session = Depends(get_db)):
    print(id_number)

    # Get the current date and time
    current_datetime = datetime.now()
    checkout_time_limit = datetime.combine(datetime.today(), time(16, 30))  # 4:30 PM

    # Check if the current time is after 4:30 PM
    if current_datetime > checkout_time_limit:
        # Get today's date in the required format
        today_date = date.today().strftime("%Y-%m-%d")

        # Check if the user ID exists in the database
        user = db.query(models.User).filter(models.User.id == id_number).first()

        if user:
            # Check if the user has already signed in today
            existing_attendance = db.query(models.Attendance).filter(
                models.Attendance.user_id == id_number,
                models.Attendance.sign_in_date == today_date
            ).first()

            if existing_attendance:
                print("User has already signed in today.")
                # User exists and has signed in today, use the existing sign_in_time for checkout
                sign_in_time = existing_attendance.sign_in_time

                # Create a full datetime object for sign_out_time
                sign_out_time = datetime.combine(datetime.today(), current_datetime.time())

                # Create attendance record for checkout
                attendance = models.Attendance(user_id=id_number, sign_in_time=sign_in_time, sign_out_time=sign_out_time,sign_in_date=today_date, sign_out_date=today_date)
                db.add(attendance)
                db.commit()
                print("The user has successfully checked out.")
                message = "You have checked out successfully: {}".format(id_number)
            else:
                # User exists but has not signed in today, raise an error
                print("User has not signed in today.")
                message = "Error: User ID {} has not signed in today.".format(id_number)
                raise HTTPException(status_code=400, detail=message)
        else:
            # User does not exist, raise an error
            print("There is an error, user is not in our database")
            message = "Error: User ID {} not found in the database.".format(id_number)
            raise HTTPException(status_code=404, detail=message)
    else:
        # User is attempting to check out before 4:30 PM, raise an error
        message = "Error: You can only check out after 4:30 PM."
        raise HTTPException(status_code=400, detail=message)

    # Pass the message to the template response
    return templates.TemplateResponse("Attendance Ui/signup.html", {"request": request, "message": message})


