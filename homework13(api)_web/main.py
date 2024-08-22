import cloudinary
import src.crud as crud
import cloudinary.uploader
from slowapi import Limiter
import src.schemas as schemas
from src.config import config
from sqlalchemy.orm import Session
from src.auth import router as auth_router
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from src.database.database import engine, Base, get_db
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.add_middleware(SlowAPIMiddleware)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config(
  cloud_name=config.CLOUDINARY_CLOUD_NAME,
  api_key=config.CLOUDINARY_API_KEY,
  api_secret=config.CLOUDINARY_API_SECRET
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.post("/upload-avatar/", response_model=schemas.User)
def upload_avatar(file: UploadFile, db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(crud.get_current_active_user)):
    result = cloudinary.uploader.upload(file.file, folder="avatars/")
    current_user.avatar_url = result["secure_url"]
    db.commit()
    return current_user

@app.post("/contacts/", response_model=schemas.Contact)

@limiter.limit("5/minute")
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(crud.get_current_active_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.get("/contacts/", response_model=list[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(crud.get_current_active_user)):

    return crud.get_contacts(db, skip=skip, limit=limit, user_id=current_user.id)

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(crud.get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate,
                   db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact)

@app.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(crud.get_current_active_user)):
    db_contact = crud.delete_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.get("/contacts/search/", response_model=list[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(crud.get_current_active_user)):
    return crud.search_contacts(db, query=query, user_id=current_user.id)

@app.get("/contacts/upcoming_birthdays/", response_model=list[schemas.Contact])
def get_upcoming_birthdays(db: Session = Depends(get_db),
                           current_user: schemas.User = Depends(crud.get_current_active_user)):
    return crud.get_upcoming_birthdays(db, user_id=current_user.id)