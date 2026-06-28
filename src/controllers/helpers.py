
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
