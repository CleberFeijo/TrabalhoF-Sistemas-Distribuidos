import multiprocessing

from fastapi import Request, Response
from gunicorn.arbiter import Arbiter
from typing import Any, Callable, Literal, Mapping, Optional, Sequence, Union

from common.classes import UNDEFINED
from core.loggers import Loggers
from core.settings import env_settings

from ...classes import ServerOptions

__all__ = 'GunicornOptions',


class GunicornOptions(ServerOptions):
    """
    Classe contendo as opções utilizadas para a criação de um servidor Gunicorn.

    Argumentos que não devem ser utilizados programaticamente ou que referem-se
    a arquivos de configuração não estarão listados no construtor desta classe.

    - Baseado na versão `20.1.0` do Gunicorn.
    """

    __defaults__ = {
        'accesslog': '-',
        'bind': f'0.0.0.0:{env_settings.APP_PORT}',
        'graceful_timeout': 120,
        'logconfig_dict': Loggers.config,
        'timeout': 180,
        'workers': env_settings.APP_WORKERS or multiprocessing.cpu_count() * 2,
        'worker_class': 'uvicorn.workers.UvicornWorker',
    }
    """
    Correlaciona um parâmetro de instanciação com o valor padrão customizado,
    diferente do padrão definido pelo Gunicorn.
    """

    # noinspection PyUnusedLocal
    # OBS: valores são acessados através de vars().
    def __init__(
            self,
            # Para Devs.:
            #   Os kwargs comentados são argumentos válidos mas não
            #   documentados - havendo a necessidade de utilizar alguma dessas
            #   opções, descomente a linha da opção e adicione sua respectiva
            #   documentação!

            use_defaults: bool = False,
            *,
            accesslog: Optional[str] = UNDEFINED,
            access_log_format: str = UNDEFINED,
            bind: Union[str, Sequence[str]] = UNDEFINED,
            backlog: int = UNDEFINED,
            # ca_certs: str = UNDEFINED,
            capture_output: bool = UNDEFINED,
            # cert_reqs: int = UNDEFINED,
            # certfile: str = UNDEFINED,
            chdir: Union[str, bytes] = UNDEFINED,
            child_exit: Callable[[Arbiter, Any], None] = UNDEFINED,
            # ciphers: str = UNDEFINED,
            daemon: bool = UNDEFINED,
            # default_proc_name: str = UNDEFINED,
            disable_redirect_access_to_syslog: bool = UNDEFINED,
            # do_handshake_on_connect: bool = UNDEFINED,
            # dogstatsd_tags: str = UNDEFINED,
            # enable_stdio_inheritance: bool = UNDEFINED,
            errorlog: Optional[str] = UNDEFINED,
            forwarded_allow_ips: str = UNDEFINED,
            graceful_timeout: int = UNDEFINED,
            group: Union[int, str, None] = UNDEFINED,
            initgroups: bool = UNDEFINED,
            keepalive: int = UNDEFINED,
            # keyfile: str = UNDEFINED,
            limit_request_field_size: int = UNDEFINED,
            limit_request_fields: int = UNDEFINED,
            limit_request_line: int = UNDEFINED,
            logconfig_dict: Mapping = UNDEFINED,
            logger_class: str = UNDEFINED,
            loglevel: Literal['debug', 'info', 'warning', 'error', 'critical'] = UNDEFINED,
            max_requests: int = UNDEFINED,
            max_requests_jitter: int = UNDEFINED,
            nworkers_changed: Callable[[Arbiter, int, int], None] = UNDEFINED,
            on_exit: Callable[[Arbiter], None] = UNDEFINED,
            on_reload: Callable[[Arbiter], None] = UNDEFINED,
            on_starting: Callable[[Arbiter], None] = UNDEFINED,
            paste: str = UNDEFINED,
            pidfile: str = UNDEFINED,
            post_fork: Callable[[Any], None] = UNDEFINED,
            post_request: Callable[[Any, Request, Any, Response], None] = UNDEFINED,
            post_worker_init: Callable[[Any], None] = UNDEFINED,
            pre_exec: Callable[[Arbiter], None] = UNDEFINED,
            pre_fork: Callable[[Arbiter, Any], None] = UNDEFINED,
            pre_request: Callable[[Any, Request], None] = UNDEFINED,
            preload_app: bool = UNDEFINED,
            # proc_name: str = UNDEFINED,
            proxy_allow_ips: str = UNDEFINED,
            proxy_protocol: bool = UNDEFINED,
            # pythonpath: str = UNDEFINED,
            raw_paste_global_conf: list[str] = UNDEFINED,
            reload: bool = UNDEFINED,
            reload_engine: Literal['auto', 'poll', 'inotify'] = UNDEFINED,
            reload_extra_files: list[Any] = UNDEFINED,
            reuse_port: bool = UNDEFINED,
            secure_scheme_headers: Mapping[str, Any] = UNDEFINED,
            sendfile: bool = UNDEFINED,
            spew: bool = UNDEFINED,
            # ssl_version = UNDEFINED,
            # statsd_host: str = UNDEFINED,
            # statsd_prefix: str = UNDEFINED,
            # strip_header_spaces: bool = UNDEFINED,
            # suppress_ragged_eofs: bool = UNDEFINED,
            # syslog: bool = UNDEFINED,
            # syslog_addr: str = UNDEFINED,
            # syslog_facility: str = UNDEFINED,
            # syslog_prefix: str = UNDEFINED,
            threads: int = UNDEFINED,
            timeout: int = UNDEFINED,
            # tmp_upload_dir: str = UNDEFINED,
            umask: int = UNDEFINED,
            user: Union[int, str, None] = UNDEFINED,
            when_ready: Callable[[Arbiter], None] = UNDEFINED,
            workers: int = UNDEFINED,
            worker_abort: Callable[[Any], None] = UNDEFINED,
            worker_class: str = UNDEFINED,
            worker_connections: int = UNDEFINED,
            worker_exit: Callable[[Arbiter, Any], None] = UNDEFINED,
            worker_int: Callable[[Any], None] = UNDEFINED,
            worker_tmp_dir: str = UNDEFINED,
    ):
        """

        :param accesslog:
            Caminho para o arquivo de log de acessos.
            Quando ``'-'`` indica que deve logar no terminal (*stdout*).
            O valor padrão do Gunicorn é ``None``.

        :param access_log_format:
            Formato de logging para o log de acessos.

        :param bind:
            O(s) *socket(s)* a ser(em) vinculado(s).
            Deve possuir um dos seguintes formatos: ``HOST``, ``HOST:PORT``,
            ``unix:PATH``, ``fd://FD``.
            Se a variável de ambiente ``PORT`` for definida, o valor padrão
            do Gunicorn é ``['0.0.0.0:$PORT']`` - caso contrário, é
            ``['127.0.0.1:8000']``.

        :param backlog:
            Determina o número máximo de conexões pendentes para serem
            servidas. Exceder esse número resultará no cliente recebendo um
            erro ao tentar se conectar.
            O valor padrão do Gunicorn é ``2048``.

        :param capture_output:
            Redireciona os outputs de *stdout/stderr* para o arquivo
            especificado em ``errorlog``.
            O valor padrão do Gunicorn é ``False``.

        :param chdir:
            Muda para o diretório antes de iniciar as aplicações.
            O valor padrão do Gunicorn é ``gunicorn.util.getcwd()``.

        :param child_exit:
            *Hook* chamado logo após um worker ser finalizado, no processo
            principal.

        :param daemon:
            Quando ``True``, o Gunicorn será executado em segundo plano
            (*daemon*), desacoplando o servidor do terminal (impede a exibição
            de logs e informações no terminal).
            O valor padrão do Gunicorn é ``False``.

        :param disable_redirect_access_to_syslog:
            Quando ``True``, desabilita o redirecionamento dos logs de acesso
            para o *syslog*.
            O valor padrão do Gunicorn é ``False``.

        :param errorlog:
            Caminho para o arquivo de log de acessos.
            Quando ``'-'`` indica que deve logar no terminal (*stderr*).
            O valor padrão do Gunicorn é ``'-''``.

        :param forwarded_allow_ips:
            String (estilo lista, separado por ",") contendo quais endereços IP
            são permitidos para lidar com ``secure_scheme_headers``.
            Use "*" para desabilitar a checagem de IP.
            Se a variável de ambiente ``FORWARDED_ALLOW_IPS`` for definida,
            o valor padrão do Gunicorn é ``$FORWARDED_ALLOW_IPS`` - caso
            contrário, é ``"127.0.0.1"``.

        :param graceful_timeout:
            Tempo máximo (em segundos) para o *"graceful shutdown"* de um
            worker. Após receber um sinal de reinicialização, os workers têm
            esse tempo para terminar de executar as requisições em andamento -
            os workers que continuarem "vivos" após esse tempo serão forçados a
            finalizar.
            O valor padrão do Gunicorn é `30`.

        :param group:
            Altera os processos dos *workers* para rodarem como neste grupo.
            O valor padrão do Gunicorn é ``os.getegid()``.

        :param keepalive:
            Tempo (em segundos) para esperar pela próxima requisição em uma
            conexão *keep-alive*.
            O valor padrão do Gunicorn é `2`.

        :param initgroups:
            Quando ``True``, define a lista de grupos dos *workers* com base
            em todos os grupos que o usuário especificado é membro.
            O valor padrão do Gunicorn é `False`.

        :param limit_request_field_size:
            Limita o tamanho de um campo em um cabeçalho de uma requisição HTTP.
            Quando ``0``, indica que não há limite, porém abre a possibilidade
            para ataques *DDOS*.
            O valor padrão do Gunicorn é ``8190``.

        :param limit_request_fields:
            Limita o número de cabeçalhos em uma requisição.
            Definir um limite máximo pode auxiliar na prevenção de ataques *DDOS*.
            Deve ser um valor entre ``100`` e ``32768``.
            O valor padrão do Gunicorn é ``100``.

        :param limit_request_line:
            Limita o tamanho de uma requisição HTTP (em bytes).
            Definir um tamanho máximo pode auxiliar na prevenção de qualquer
            ataque *DDOS*.
            Deve ser um valor entre ``0`` (sem limite) e ``8190``.
            O valor padrão do Gunicorn é ``4094``.

        :param loglevel:
            Nível de granularidade dos logs.
            O valor padrão do Gunicorn é ``'info'``.

        :param logger_class:
            Caminho até a classe de logger usada para logar os eventos no
            *Gunicorn*.
            O valor padrão do Gunicorn é ``'gunicorn.glogging.Logger'``.

        :param logconfig_dict:
            Dicionário contendo as configurações de logging, usando configuração
            padrão utilizada pelo python.
            O valor padrão do Gunicorn é ``{}``.

        :param max_requests:
            Número máximo de requisições que um *worker* vai processar antes
            de reiniciar - Quando `0`, *workers* não serão reiniciados
            automaticamente.
            Isto ajuda a reduzir a possibilidade de *memory leaks*.
            O valor padrão do Gunicorn é ``0``.

        :param max_requests_jitter:
            Número máximo de *jitter* para adicionar à configuração
            ``max_requests``, com o intuito de impedir que todos os *workers*
            reiniciem ao mesmo tempo.
            O valor padrão do Gunicorn é ``0``.

        :param nworkers_changed:
            *Hook* chamado quando o número de workers é alterado.

        :param on_exit:
            *Hook* chamado antes de sair do gunicorn.

        :param on_reload:
            *Hook* chamado durante o recarregamento dos *workers* via *SIGHUP*.

        :param on_starting:
            *Hook* chamado antes do processo mestre ser inicializado.

        :param pidfile:
            Nome do arquivo a ser utilizado como arquivo *PID*.
            Quando não definido, o arquivo *PID* não será escrito.
            O valor padrão do Gunicorn é ``None``.

        :param post_fork:
            *Hook* chamado logo após um *worker* ser criado a partir do
            processo principal.

        :param post_request:
            *Hook* chamado após o *worker* processar uma requisição.

        :param post_worker_init:
            *Hook* chamado logo após ter inicializado a aplicação.

        :param pre_exec:
            *Hook* chamado antes do processo principal começar a server
            requisições.

        :param pre_fork:
            *Hook* chamado antes de um *worker* ser criado a partir do processo
            principal.

        :param pre_request:
            *Hook* chamado antes de um *worker* processar uma requisição.

        :param preload_app:
            Quando ``True``, carrega o código da aplicação antes dos processos
            dos *workers* serem separados.
            Este tipo de ação pode reduzir o consumo de RAM e acelerar o tempo
            de inicialização do servidor.
            O valor padrão do Gunicorn é ``False``.

        :param proxy_allow_ips:
            String (estilo lista, separado por ",") contendo quais endereços IP
            são permitidos para aceitar requisições proxy.
            Use "*" para desabilitar a checagem de IP.
            O valor padrão do Gunicorn é ``"127.0.0.1"``.

        :param proxy_protocol:
            Quando ``True``,permite a deteccção de protocolo PROXY.
            O valor padrão do Gunicorn é ``False``.

        :param reload:
            Restarta os workers quando o código muda (Voltado para ambiente
            de desenvolvimento).
            **OBS**: Não parece funcionar corretamente com workers do Uvicorn.
            O valor padrão do Gunicorn é ``False``.

        :param reload_engine:
            *Engine* usada para restartar os workers quando
            ``reload`` for ``True``.
            O valor padrão do Gunicorn é ``"auto"``.

        :param reload_extra_files:
            Lista os arquivos adicionais que devem ser monitorados pela lógica
            de *reload* (Somente quando ``reload`` for ``True``).
            O valor padrão do Gunicorn é ``[]``.

        :param reuse_port:
            Quando ``True``, permite que múltiplos *workers* se vinculem à
            mesma porta simultâneamente, melhorando o *load balance* e o
            controle de conexões.
            Entretanto, possui baixa compatibilidade com SO e incrementa a
            complexidade nos quesitos "controle" e "configuração" do Gunicorn.
            O valor padrão do Gunicorn é ``False``.

        :param secure_scheme_headers:
            Define os cabeçalhos HTTP que indicam se a conexão é segura (HTTPS).

        :param sendfile:
            Quando ``True``, desabilita o uso de ``sendfile()`` (Sim, possui a
            lógica inversa onde ``True`` desabilita).
            O valor padrão do Gunicorn é ``False``.

        :param spew:
            Quando ``True``, instala uma função que emite TODA linha executada
            pelo servidor.
            **OBS**: Deve ser usada SOMENTE em ambiente de desenvolvimento
            ou *debugging*.
            O valor padrão do Gunicorn é ``False``.

        :param threads:
            Número de *threads* utilizadas pelos *workers*.
            Só funciona caso ``worker_class`` seja do tipo ``Gthread``.
            O valor padrão do Gunicorn é ``1``.

        :param timeout:
            Tempo máximo (em segundos) que um worker tem para processar uma
            requisição antes que seja considerado um *"timeout"*.
            Se o tempo de processamento da requisição exceder o valor
            especificado, o worker encerrará a conexão e o cliente receberá um
            erro de timeout.
            O valor padrão do Gunicorn é ``30``.

        :param umask:
            Define as permissões padrão para os arquivos criados pelos
            *workers*.
            O valor padrão do Gunicorn é ``0``.

        :param user:
            Altera os processos dos *workers* para rodarem como este usuário.
            O valor padrão do Gunicorn é ``os.geteuid()``.

        :param when_ready:
            *Hook* chamado após o servidor ser iniciado.

        :param workers:
            Número de *workers* para lidar com as requisições.
            Costuma possuir um valor entre 2 a 4 vezes o número de núcleos.
            Se a variável de ambiente ``WEB_CONCURRENCY`` for definida, utiliza
            este valor como padrão - caso contrário, é ``1``.

        :param worker_abort:
            *Hook* chamado quando um *worker* recebe o sinal *SIGABRT*.

        :param worker_class:
            Classe do worker a ser utilizada.
            Junto ao Uvicorn, normalmente é utilizada
            `uvicorn.workers.UvicornWorker`.
            O valor padrão do Gunicorn é ``sync``.

        :param worker_connections:
            Número máximo de clientes simultâneos, mas somente para workers do
            tipo ``Eventlet`` ou ``Gevent``.
            O valor padrão do Gunicorn é ``1000``.

        :param worker_exit:
            *Hook* chamado logo após o processo de um worker ser finalizado.

        :param worker_int:
            *Hook* chamado logo após um worker sair ao receber um sinal
            *SIGINT* ou *SIGQUIT*.

        :param worker_tmp_dir:
            Diretório temporário utilizado para guardar o arquivo de
            *heartbeat* do *worker*.
            Quando ``None``, não será utilizado um diretório temporário.
            O valor padrão do Gunicorn é ``None``.
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
