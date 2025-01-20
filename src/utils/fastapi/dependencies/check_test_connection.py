from fastapi import Request

__all__ = 'check_test_connection',


def check_test_connection(request: Request) -> bool:
    """
    Retorna um booleano indicando se a requisição é feita a partir de um
    cliente de teste do httpx (usado pelo pytest + fastapi).

    - Serve, principalmente, para definir quais operações podem ou não ser
      realizadas quando uma API estiver sendo testada, ou qual cliente mongodb
      utilizar.
    """
    return request.client[0] == 'testclient'
