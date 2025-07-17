from sqlalchemy.orm import Session
from app.db.models.solicitacao import Solicitacao
from app.schemas.solicitacao import SolicitacaoCreate

class CRUDSolicitacao:
    def create(self, db: Session, obj_in: SolicitacaoCreate):
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        db_obj = Solicitacao(**obj_data)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

    def get(self, db: Session, id: int):
        return db.query(Solicitacao).filter(Solicitacao.id == id).first()

    def get_by_contact(self, db: Session, contact_id: int):
        return db.query(Solicitacao).filter(Solicitacao.contact_id == contact_id).all()

crud_solicitacao = CRUDSolicitacao()