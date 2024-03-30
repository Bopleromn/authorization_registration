from fastapi import Depends, FastAPI, Request, APIRouter, HTTPException
from sqlalchemy.orm import Session
from db import get_db
import request_models
import table_models
import status


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('', status_code=status.HTTP_302_FOUND)
async def handle_user_get(email: str, password: str,
                          db: Session=Depends(get_db)):
    user = db.query(table_models.User).filter(table_models.User.email == email).filter(table_models.User.password == password).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='user not found')
         
    return {'data': user}
    
    
@router.post('', status_code=status.HTTP_201_CREATED)
async def handle_user_post(user: request_models.UserAdd,
                           db: Session=Depends(get_db)):
    new_user = table_models.User(**user.model_dump())
    
    db.add(new_user)
    
    try:
        db.commit()
        db.refresh(new_user)
        
        return {'data': new_user}
    except Exception as e:
        return {'response': False}
    
    
@router.put('', status_code=status.HTTP_202_ACCEPTED)
async def hande_user_put(email: str, password: str, new_user: request_models.UserAdd,
                         db: Session=Depends(get_db)):
    query = db.query(table_models.User).filter(table_models.User.email == email).filter(table_models.User.password == password)
    
    old_user = query.first()
    
    if old_user is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='user not found')
    
    query.update(new_user.model_dump(), synchronize_session=False)
    
    try:
        db.commit()
        
        updated_user = db.query(table_models.User).filter(table_models.User.email == new_user.email).filter(table_models.User.password == new_user.password).first()
        
        return {'data': updated_user}
    except:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, 
                            detail='could not update user')
    
    
@router.delete('', status_code=status.HTTP_204_NO_CONTENT, )
async def handle_user_delete(email: str, password: str,
                             db: Session=Depends(get_db)):
    user = db.query(table_models.User).filter(table_models.User.email == email).filter(table_models.User.password == password).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='user not found')
    
    db.delete(user)
    db.commit()