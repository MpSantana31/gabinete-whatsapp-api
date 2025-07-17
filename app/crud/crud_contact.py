from sqlalchemy.orm import Session
from app.db.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from datetime import datetime

class CRUDContact:
    def create(self, db: Session, contact: ContactCreate) -> Contact:
        db_contact = Contact(
            phone_number=contact.phone_number,
            name=contact.name,
            ia_active=contact.ia_active
        )
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact

    def get_by_phone(self, db: Session, phone_number: str) -> Contact:
        print(f"--- [DEBUG] Buscando no DB por phone_number: '{phone_number}' ---")
    
        result = db.query(Contact).filter(Contact.phone_number == phone_number).first()
        
        if result:
            print("--- [DEBUG] Contato encontrado! ---")
        else:
            print("--- [DEBUG] Contato NÃO encontrado pela query. ---")
            
        return result

    def update(
        self, 
        db: Session, 
        db_contact: Contact, 
        contact: ContactUpdate
    ) -> Contact:
        update_data = contact.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_contact, field, value)
        db.commit()
        db.refresh(db_contact)
        return db_contact

    def toggle_ia_status(self, db: Session, phone_number: str) -> Contact:
        contact = self.get_by_phone(db, phone_number)
        if contact:
            contact.ia_active = not contact.ia_active
            db.commit()
            db.refresh(contact)
        return contact
    
    def get_or_create(self, db: Session, phone_number: str) -> Contact:
        """Obtém ou cria um contato se não existir"""
        contact = self.get_by_phone(db, phone_number)
        if not contact:
            contact = self.create(db, ContactCreate(
                phone_number=phone_number,
                ia_active=True,
                updated_at=datetime.now(),
                status=True
            ))
        return contact

    def get_all(self, db: Session) -> list[Contact]:
        return db.query(Contact).all()

crud_contact = CRUDContact()