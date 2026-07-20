import logging 


logging.basicConfig(filename='services.log', level=logging.INFO)





def decorator(foo):
    def square(n: int):
        return n * n

    def wrapper(*args, **kwargs):
        summation = foo(*args)

        print(foo.__name__ + ' ' + square.__name__ + ' were called')
        return square(summation)

    return wrapper


@decorator
def func(a, b):
    return a + b

logging.info(f'{func(10, 5)}')

print(func(10, 5), func.__name__)