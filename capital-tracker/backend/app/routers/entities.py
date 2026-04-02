from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entity import Entity
from app.schemas.entity import EntityCreate, EntityUpdate, EntityResponse, EntityWithAccounts

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("", response_model=list[EntityResponse])
def list_entities(db: Session = Depends(get_db)):
    return db.query(Entity).order_by(Entity.name).all()


@router.post("", response_model=EntityResponse, status_code=201)
def create_entity(data: EntityCreate, db: Session = Depends(get_db)):
    entity = Entity(name=data.name, entity_type=data.entity_type)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.get("/{entity_id}", response_model=EntityWithAccounts)
def get_entity(entity_id: UUID, db: Session = Depends(get_db)):
    entity = db.get(Entity, entity_id)
    if not entity:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(entity_id: UUID, data: EntityUpdate, db: Session = Depends(get_db)):
    entity = db.get(Entity, entity_id)
    if not entity:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Entity not found")
    if data.name is not None:
        entity.name = data.name
    if data.entity_type is not None:
        entity.entity_type = data.entity_type
    db.commit()
    db.refresh(entity)
    return entity
