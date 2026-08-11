from myorg.config import GREETING


def greet(name: str) -> str:
    """
    Greet someone by name:

    >>> greet('world')
    'Hello, world!'

    """
    return f'{GREETING}, {name}!'
