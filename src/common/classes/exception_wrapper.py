import re

from traceback import format_tb

from common.typealiases import Generic, ExceptionT, Type

from .serializable import Serializable

__all__ = 'ExceptionWrapper',


class ExceptionWrapper(Serializable, Generic[ExceptionT]):
    """
    Classe responsável por envelopar uma exceção e criar sua respectiva
    descrição contendo tipo, mensagem de erro e traceback.
    """

    def __init__(self, exc: ExceptionT):
        self.exc: ExceptionT = exc

    # ====================== #
    # ~~~~| Properties |~~~~ #
    # ====================== #

    @property
    def exc_type(self) -> Type[ExceptionT]:
        return type(self.exc)

    @property
    def exc_msg(self) -> str:
        return str(self.exc)

    @property
    def exc_tb(self):
        return self.exc.__traceback__

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def json_serialize(self):
        return {
            'exc_type': str(self.exc_type),
            'exc_msg': self.exc_msg,
            'exc_tb': self._get_traceback_messages(),
        }

    def _get_traceback_messages(
            self,
            include_inner_errors: bool = False,
    ) -> list[dict[str, str]]:
        """
        Cria uma lista de dicts, contendo as informações referentes ao
        traceback da exceção ocorrida;

        :param include_inner_errors: Quando False, remove do traceback as
          informações referentes à exceção ocorrida em alguma lib interna -
          porém se o erro ocorrido for inteiramente causado dentro de alguma
          lib interna, gera o traceback completo.
        """
        group_pattern = re.compile(
            r'^\s*File\s*"(?P<filepath>.+?)", line (?P<line>\d+), in '
            r'(?P<method>\S+)\n\s*(?P<code>.+)',
        )
        "Pattern para capturar os grupos detalhados."

        project_pattern = re.compile(r'^/[\w\-]+/\./')
        "Pattern para detectar se o traceback diz respeito ao projeto em si."

        full_desc = []

        for tb in reversed(format_tb(self.exc_tb)):
            match = group_pattern.search(tb)
            if not match:
                continue
            group = match.groupdict()

            # Converte a linha para int.
            group['line'] = int(group['line'])

            # Busca pelo diretório do projeto no path do arquivo do traceback.
            # Se não encontrar, quebra o fluxo (para remover as infos. de erros
            # internos de outras libs).
            if not include_inner_errors and not project_pattern.search(group['filepath']):
                break

            group['filepath'] = project_pattern.sub('/', group['filepath'])
            full_desc.append(group)

        # Se não gerar nenhum traceback e estiver excluindo erros internos
        # do resultado, tenta gerar o traceback para a lib interna.
        if not full_desc and not include_inner_errors:
            return self._get_traceback_messages(include_inner_errors=True)

        # Retorna à ordem original do traceback.
        return list(reversed(full_desc))
