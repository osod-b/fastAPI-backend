    
# def _give_user_root_rules(username: str, db: Session):
#     user = db.query(UserModel).filter(UserModel.username == username.value).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't find a user")
#     try:
#         user.root = True
#         db.commit()
#         db.refresh(user)
#     except IntegrityError:
#         raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Couldn't implement changes")

