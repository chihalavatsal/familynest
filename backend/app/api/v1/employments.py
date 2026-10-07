import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.employment import Employment
from app.schemas.employment import EmploymentCreate, EmploymentUpdate, EmploymentResponse
from app.services.authz_service import AuthzService
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/people/{person_id}/employments", tags=["employments"])

@router.get("", response_model=List[EmploymentResponse])
def list_employments(person_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_read_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to read this person's employments")
    return db.execute(select(Employment).where(Employment.person_id == person_id).order_by(Employment.start_date.desc())).scalars().all()

@router.post("", response_model=EmploymentResponse)
def create_employment(person_id: uuid.UUID, data: EmploymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_edit_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this person")
    
    emp = Employment(
        person_id=person_id,
        employer_name=data.employer_name,
        job_title=data.job_title,
        department=data.department,
        location=data.location,
        employment_type=data.employment_type,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        is_current=data.is_current
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

@router.patch("/{emp_id}", response_model=EmploymentResponse)
def update_employment(person_id: uuid.UUID, emp_id: uuid.UUID, data: EmploymentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_edit_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this person")
    
    emp = db.get(Employment, emp_id)
    if not emp or emp.person_id != person_id:
        raise HTTPException(status_code=404, detail="Employment not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(emp, key, value)
        
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employment(person_id: uuid.UUID, emp_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    authz = AuthzService(db)
    if not authz.can_edit_person(current_user.id, person_id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this person")
    emp = db.get(Employment, emp_id)
    if not emp or emp.person_id != person_id:
        raise HTTPException(status_code=404, detail="Employment not found")
    db.delete(emp)
    db.commit()
