import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.education import Education
from app.schemas.education import EducationCreate, EducationUpdate, EducationResponse
from app.services.authz_service import AuthzService
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/people/{person_id}/educations", tags=["educations"])

@router.get("", response_model=List[EducationResponse])
def list_educations(person_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_read_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to read this person's education history")
    return db.execute(select(Education).where(Education.person_id == person_id).order_by(Education.start_date.desc().nulls_last())).scalars().all()

@router.post("", response_model=EducationResponse)
def create_education(person_id: uuid.UUID, data: EducationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_edit_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this person")
    
    edu = Education(
        person_id=person_id,
        institution=data.institution,
        degree=data.degree,
        field_of_study=data.field_of_study,
        location=data.location,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date
    )
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu

@router.delete("/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(person_id: uuid.UUID, edu_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_edit_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this person")
    edu = db.get(Education, edu_id)
    if not edu or edu.person_id != person_id:
        raise HTTPException(status_code=404, detail="Education record not found")
    db.delete(edu)
    db.commit()
