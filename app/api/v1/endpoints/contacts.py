from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.contact import Contact, ContactCreate, ContactUpdate
from app.crud.crud_contact import crud_contact

router = APIRouter()

@router.post("/", response_model=Contact)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return crud_contact.create(db, contact)

@router.get("/", response_model=list[Contact])
def read_contacts(db: Session = Depends(get_db)):
    return crud_contact.get_all(db)

@router.get("/{phone_number}", response_model=Contact)
def read_contact(phone_number: str, db: Session = Depends(get_db)):
    contact = crud_contact.get_by_phone(db, phone_number)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.patch("/{phone_number}", response_model=Contact)
def update_contact(
    phone_number: str, 
    contact: ContactUpdate, 
    db: Session = Depends(get_db)
):
    db_contact = crud_contact.get_by_phone(db, phone_number)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud_contact.update(db, db_contact, contact)

@router.post("/{phone_number}/toggle-ia", response_model=Contact)
def toggle_ia_status(phone_number: str, db: Session = Depends(get_db)):
    return crud_contact.toggle_ia_status(db, phone_number)
