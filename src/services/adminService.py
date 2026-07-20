from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import UserModel    


# #root_user: 0/1

class RootUserService():
    def __init__(self, async_session):
        self.db = async_session
    
    def export_csv():
        ...

    def export_excel():
        ...
    
    def clean_db():
        ...
    
    def change_user_pwd():
        ...
    
    def change_user_username():
        ...

    def change_user_email():
        ...

    def delete_user():
        ...

    def give_root(username: str, db: Session):
        user = db.query(UserModel).filter(UserModel.username == username.value).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't find a user")
        try:
            user.root = True
            db.commit()
            db.refresh(user)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Couldn't implement changes")




# @app.get("/app/users")
# def get_all_users(limit: int = None, db: Session = get_db()):
#     total = db.query(func.count(UserModel.id)).scalar()

#     if limit is not None:
#         if limit > total:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Limit {limit} exceeds total user count of {total}",
#             )
#         users = db.query(UserModel).order_by(UserModel.id).limit(limit).all()
#     else:
#         users = db.query(UserModel).order_by(UserModel.id).all()

#     return {"entity": {"state": "Successfully found", "count": len(users), "users": users}}


# @app.delete("/app/clear_database")
# def clear_database(db: Session = get_db()):
#     deleted = db.query(UserModel).delete()
#     db.commit()
#     return {"message": f"Database cleared. {deleted} rows removed."}



# @auth.delete('root/delete', response_model=UserDelete)
# def delete_user():
#     return JSONResponse()



# def delete_user(user_id: str, cookies: Optional[str] = Cookie(None, alias='access_token'), db: Session = Depends(get_db)):

#     #take cookies, verify jwt, find actual user in db check whether he has root = 1, then if he has we check the case doesn't he want delete himself,
#     #if so, we just ban restrict this action, if not, then we delete or deactivate this user profile.

#     user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     db.delete(user)
#     db.commit()
    
#     return {"status": status.HTTP_202_ACCEPTED,
#             "message": 'Deleted successfully'}
