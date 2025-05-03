from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

import models
import schemas
import crud
import auth
from database import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "https://your-production-frontend.com"  # Optional production origin
]



Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploads"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs(UPLOAD_DIR, exist_ok=True)


app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.put("/users/me", response_model=schemas.UserOut)
def update_user_profile(
    user_update: schemas.UserUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    user = crud.update_user_profile(db, current_user.id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/items", response_model=schemas.ItemOut)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_item(db, current_user.id, item)


@app.get("/items", response_model=List[schemas.ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.list_items(db)


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "url": f"/uploads/{file.filename}"}


@app.get("/")
def root():
    return {"message": "FakeLive backend is running!"}
