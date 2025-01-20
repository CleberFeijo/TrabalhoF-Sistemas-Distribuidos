from typing import Literal

from common.classes import UNDEFINED
from core.settings import env_settings, env

from ...classes import ServerOptions

__all__ = 'UvicornOptions',


class UvicornOptions(ServerOptions):
    """
    Classe contendo as opções utilizadas para a criação de um servidor Uvicorn.

    Argumentos que não devem ser utilizados programaticamente ou que referem-se
    a arquivos de configuração não estarão listados no construtor desta classe.

    - Baseado na versão `0.17.6` do Uvicorn.
    """

    __defaults__ = {
        'host': '0.0.0.0',
        'port': int(env_settings.APP_PORT),
        'reload': env.is_dev(),
        'workers': 1,
    }
    """
    Correlaciona um parâmetro de instanciação com o valor padrão customizado,
    diferente do padrão definido pelo Uvicorn.
    """

    @property
    def use_app_path(self) -> bool:
        return bool(self.get('reload') or self.get('workers'))

    # noinspection PyUnusedLocal
    # OBS: valores são acessados através de vars().
    def __init__(
            self,
            use_defaults: bool = False,
            *,
            # Para Devs.:
            #   Os kwargs comentados são argumentos válidos mas não
            #   documentados - havendo a necessidade de utilizar alguma dessas
            #   opções, descomente a linha da opção e adicione sua respectiva
            #   documentação!

            # access_log: bool = UNDEFINED,
            # app_dir: str = UNDEFINED,
            # backlog: int = UNDEFINED,
            # date_header: bool = UNDEFINED,
            # debug: bool = UNDEFINED,
            # factory: bool = UNDEFINED,
            # fd: int = UNDEFINED,
            # forwarded_allow_ips: str = UNDEFINED,
            # headers: list[str] = UNDEFINED,
            host: str = UNDEFINED,
            # http: str = UNDEFINED,
            # interface: str = UNDEFINED,
            # lifespan: str = UNDEFINED,
            # limit_concurrency: int = UNDEFINED,
            # limit_max_requests: int = UNDEFINED,
            # log_config: str = UNDEFINED,
            log_level: Literal['debug', 'info', 'warning', 'error', 'critical'] = UNDEFINED,
            # loop: str = UNDEFINED,
            port: int = UNDEFINED,
            # proxy_headers: bool = UNDEFINED,
            reload: bool = UNDEFINED,
            # reload: bool = UNDEFINED,
            # reload_delay: float = UNDEFINED,
            reload_dirs: list[str] = UNDEFINED,
            # reload_excludes: list[str] = UNDEFINED,
            # reload_includes: list[str] = UNDEFINED,
            # root_path: str = UNDEFINED,
            # server_header: bool = UNDEFINED,
            # ssl_ca_certs: str = UNDEFINED,
            # ssl_certfile: str = UNDEFINED,
            # ssl_cert_reqs: int = UNDEFINED,
            # ssl_ciphers: str = UNDEFINED,
            # ssl_keyfile: str = UNDEFINED,
            # ssl_keyfile_password: str = UNDEFINED,
            # ssl_version: int = UNDEFINED,
            # timeout_keep_alive: int = UNDEFINED,
            # uds: str = UNDEFINED,
            # use_colors: bool = UNDEFINED,
            workers: int = UNDEFINED,
            # ws: str = UNDEFINED,
            # ws_max_size: int = UNDEFINED,
            # ws_per_message_deflate: bool = UNDEFINED,
            # ws_ping_interval: float = UNDEFINED,
            # ws_ping_timeout: float = UNDEFINED,
    ):
        """

        :param use_defaults:
            Quando ``True``, permite o preenchimento automático de alguns
            parâmetros com valores diferentes do padrão do Uvicorn, com base
            no .env e na recorrência entre projetos.

        :param host:
            Endereço que o servidor Uvicorn será vinculado.

        :param port:
            Endereço e porta que o servidor Gunicorn será vinculado.

        :param reload:
            Quando True, permite o recarregamento automático do servidor ao
            detectar mudanças no código durante desenvolvimento.

        :param reload_dirs:
            Especifica quais diretórios irão observar as alterações para
            aplicação da lógica de ``reload``.

        :param log_level:
            Nível de granularidade dos logs.

        :param workers:
            Número de processos trabalhadores (*workers*) a serem iniciados.
        """
        init_kwargs = {
            k: v
            for k, v in vars().items()
            if k not in ('self', 'use_defaults')
        }

        if use_defaults:
            for k, v in self.__defaults__.items():
                if init_kwargs.get(k, UNDEFINED) == UNDEFINED:
                    init_kwargs[k] = v

        super().__init__(**init_kwargs)
