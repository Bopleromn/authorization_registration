from random import randint
from fastapi import Depends, FastAPI, Request, APIRouter, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from helpers import send_email
from request_models import UserBase as UserJson
from table_models import User as UserTable
from table_models import VerificationCodes as VerificationCodesTable
import status


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('')
async def handle_user_get(email: str, password: str, db: Session=Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.email == email).filter(UserTable.password == password).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='user not found')
         
    return {'data': user}
    
    
@router.post('')
async def handle_user_post(user: UserJson, db: Session=Depends(get_db)):
    new_user = UserTable(**user.model_dump())
    
    db.add(new_user)
    
    try:
        db.commit()
        db.refresh(new_user)
        
        return {'data': new_user}
    except Exception as e:
        raise HTTPException(
            status_code=409,
            detail='user with that email already exists'
        )
    
    
@router.put('')
async def hande_user_put(email: str, password: str, new_user: UserJson, db: Session=Depends(get_db)):
    query = db.query(UserTable).filter(UserTable.email == email).filter(UserTable.password == password)
    
    old_user = query.first()
    
    if old_user is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='user not found')
    
    query.update(new_user.model_dump(), synchronize_session=False)
    
    try:
        db.commit()
        
        updated_user = db.query(UserTable).filter(UserTable.email == new_user.email).filter(UserTable.password == new_user.password).first()
        
        return {'data': updated_user}
    except:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, 
                            detail='could not update user')
    
    
@router.delete('')
async def handle_user_delete(email: str, password: str, db: Session=Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.email == email).filter(UserTable.password == password).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='user not found')
    
    db.delete(user)
    db.commit()
    
    
@router.get('/verification_codes/send')
async def handle_verification_code_send(email: str, db: Session = Depends(get_db)):
    # if db.query(UserTable).filter(UserTable.email).first() is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail='no such user'
    #     )
    
    current_code: int = randint(100000, 999999)
    
    recipient_info = dict(
        verification_code=current_code,
        email=email
    )
    
    try:
        await send_email(email, f"Здравствуйте, {email}. Ваш код подтверждения пришел", f"Код: {current_code}")
    except:
        raise HTTPException(
            status_code=400,
            detail='invalid email address'
        )

    query = db.query(VerificationCodesTable).filter(
        VerificationCodesTable.email == email
    )

    old_recipient_info = query.first()

    if old_recipient_info is None:
        new_recipient_info = VerificationCodesTable(**recipient_info)

        db.add(new_recipient_info)
        db.commit()

        db.refresh(new_recipient_info)

        return dict(
            data=new_recipient_info
        )

    else:

        query.update(recipient_info, synchronize_session=False)

        try:
            db.commit()

            return dict(
                data=recipient_info
            )

        except:
            raise HTTPException(
                status_code=304,
                detail='can\'t update vc'
            )
            

@router.get('/verification_codes/check')
async def handle_verification_code_check(email: str, verification_code: str, db: Session = Depends(get_db)):
    result = db.query(VerificationCodesTable).filter(VerificationCodesTable.email == email).filter(VerificationCodesTable.verification_code == verification_code).first()
    
    if result is None:
        raise HTTPException(
            status_code=409,
            detail='incorrect verification code'
        )
        
        
@router.get('/reset_password')
async def handle_reset_password(email: str, new_password: str, verification_code: str, db: Session = Depends(get_db)):
    await handle_verification_code_check(email, verification_code, db)

    user = db.query(UserTable).filter(UserTable.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=404,
            detail='user not found'
        ) 
        
    user.password = new_password
    db.commit()