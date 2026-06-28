from fastapi import APIRouter


view = APIRouter()



@view.get('users/')
def get_all_clients(number: int):
    ...