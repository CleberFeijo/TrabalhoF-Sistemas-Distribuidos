from datetime import timedelta
from kombu import Queue
from typing import Any, Literal, Mapping, Optional, Pattern, Sequence, Union

from common.classes import UNDEFINED

from .beat_schedule import *
from .queue_route import *
from .task_route import *

__all__ = 'CeleryConfig',

# https://docs.celeryq.dev/en/v5.2.7/userguide/configuration.html

TaskAnnotationT = Union[
    Mapping[str, Mapping[str, Any]],
    Sequence[Union[Mapping[str, Mapping[str, Any]], object]],
]

TaskRouterT = Union[
    str,
    dict[Union[str, Pattern], Union[str, dict]],
    tuple[Union[str, Pattern], Union[str, dict]],
]

CassandraConsistencyT = Literal['ONE', 'TWO', 'THREE', 'QUORUM', 'ALL',
                                'LOCAL_QUORUM', 'EACH_QUORUM', 'LOCAL_ONE']


class TaskPublishRetryPolicy(dict):

    # noinspection PyUnusedLocal
    # OBS: valores são acessados através do vars()
    def __init__(
            self,
            *,
            max_retries: Optional[int] = UNDEFINED,
            interval_start: Optional[float] = UNDEFINED,
            interval_step: Optional[float] = UNDEFINED,
            interval_max: Optional[float] = UNDEFINED
    ):
        """
        :param max_retries:
            Quantidade máxima de tentativas.
            Quando None, indica que o fluxo tentará infinitamente.
            O valor padrão do Celery é `3`.

        :param interval_start:
            Determina o tempo (em segundos) de espera entre cada tentativa.
            O valor padrão do Celery é `0`.

        :param interval_step:
            A cada tentativa, incrementa o tempo de espera neste valor (em segundos).
            O valor padrão do Celery é `0.2`.

        :param interval_max:
            Determina o tempo de espera máximo (em segundos) entre cada
            tentativa de reenfileiramento.
            O valor padrão do Celery é `0.2`.
        """
        super().__init__({
            k: v
            for k, v in vars().items()
            if k != 'self' and not k.startswith('_') and v != UNDEFINED
        })


class CeleryConfig(dict):

    # noinspection PyUnusedLocal
    # OBS: valores são acessados através do vars()
    def __init__(
            self,
            *,
            accept_content: Sequence[str] = UNDEFINED,
            beat_schedule: dict[str, BeatSchedule] = UNDEFINED,
            broker_url: str = UNDEFINED,
            enable_utc: bool = UNDEFINED,
            imports: Sequence[str] = UNDEFINED,
            override_backends: Optional[Mapping[str, str]] = UNDEFINED,
            result_accept_content: Optional[Sequence[str]] = UNDEFINED,
            result_backend: Optional[str] = UNDEFINED,
            result_backend_always_retry: bool = UNDEFINED,
            result_backend_base_sleep_between_retries_ms: int = UNDEFINED,
            result_backend_max_sleep_between_retries_ms: int = UNDEFINED,
            result_backend_max_retries: int = UNDEFINED,
            result_backend_transport_options: Mapping = UNDEFINED,
            result_cache_max: int = UNDEFINED,
            result_chord_join_timeout: float = UNDEFINED,
            result_chord_retry_interval: float = UNDEFINED,
            result_compression: Optional[str] = UNDEFINED,
            result_expires: Union[float, timedelta, None] = UNDEFINED,
            result_extended: bool = UNDEFINED,
            result_serializer: str = UNDEFINED,
            task_acks_late: bool = UNDEFINED,
            task_acks_on_failure_or_timeout: bool = UNDEFINED,
            task_always_eager: bool = UNDEFINED,
            task_annotations: Optional[TaskAnnotationT] = UNDEFINED,
            task_compression: Optional[str] = UNDEFINED,
            task_default_exchange: Optional[str] = UNDEFINED,
            # task_default_exchange_type: str = UNDEFINED,
            task_default_queue: Optional[str] = UNDEFINED,
            # task_default_priority: Optional[int] = UNDEFINED,
            task_default_rate_limit: Union[str, float, None] = UNDEFINED,
            # task_default_routing_key: Optional[str] = UNDEFINED,
            task_eager_propagates: bool = UNDEFINED,
            task_ignore_result: bool = UNDEFINED,
            task_protocol: Literal[1, 2] = UNDEFINED,
            task_publish_retry: bool = UNDEFINED,
            task_publish_retry_policy: Optional[TaskPublishRetryPolicy] = UNDEFINED,
            task_queues: Optional[list[Queue]] = UNDEFINED,
            task_reject_on_worker_lost: bool = UNDEFINED,
            task_remote_tracebacks: bool = UNDEFINED,
            task_routes: Union[Sequence[TaskRouterT], TaskRouterT] = UNDEFINED,
            task_serializer: str = UNDEFINED,
            task_soft_time_limit: Optional[float] = UNDEFINED,
            task_store_eager_result: bool = UNDEFINED,
            task_store_errors_even_if_ignored: bool = UNDEFINED,
            task_time_limit: Optional[float] = UNDEFINED,
            task_track_started: bool = UNDEFINED,
            timezone: str = UNDEFINED,
            worker_cancel_long_running_tasks_on_connection_loss: bool = UNDEFINED,
            worker_enable_remote_control: bool = UNDEFINED,
            worker_hijack_root_logger: bool = UNDEFINED,
            worker_max_tasks_per_child: Optional[int] = UNDEFINED,
            worker_prefetch_multiplier: int = UNDEFINED,

            # Apenas para dbdatabase backend (db+):
            database_engine_options: Mapping = UNDEFINED,
            database_short_lived_sessions: bool = UNDEFINED,
            database_table_names: Mapping[str, str] = UNDEFINED,
            database_table_schemas: Mapping[str, str] = UNDEFINED,

            # Apenas para rpc backend:
            result_persistent: bool = UNDEFINED,

            # Apenas para cache backend:
            # cache_backend_options: Mapping = UNDEFINED,

            # Apenas para mongodb backend:
            # mongodb_backend_settings: Mapping = UNDEFINED,

            # Apenas para redis backend:
            # redis_backend_health_check_interval: int = UNDEFINED,
            # redis_backend_use_ssl: Optional[Mapping] = UNDEFINED,
            # redis_max_connections: Optional[int] = UNDEFINED,
            # redis_socket_connect_timeout: Optional[float] = UNDEFINED,
            # redis_socket_timeout: float = UNDEFINED,
            # redis_retry_on_timeout: bool = UNDEFINED,
            # redis_socket_keepalive: bool = UNDEFINED,

            # Apenas para cassandra backend:
            # cassandra_servers: list = UNDEFINED,
            # cassandra_port: str = UNDEFINED,
            # cassandra_keyspace: Optional[str] = UNDEFINED,
            # cassandra_table: Optional[str] = UNDEFINED,
            # cassandra_read_consistency: Optional[CassandraConsistencyT] = UNDEFINED,
            # cassandra_write_consistency: Optional[CassandraConsistencyT] = UNDEFINED,
            # cassandra_entry_ttl: Optional[float] = UNDEFINED,
            # cassandra_auth_provider: Literal[
            #     'PlainTextAuthProvider',
            #     'SaslAuthProvider'
            # ] = UNDEFINED,
            # cassandra_auth_kwargs: Mapping = UNDEFINED,
            # cassandra_options: Mapping = UNDEFINED,

            # Apenas para s3 backend:
            # s3_access_key_id: Optional[str] = UNDEFINED,
            # s3_secret_access_key: Optional[str] = UNDEFINED,
            # s3_bucket: Optional[str] = UNDEFINED,
            # s3_base_path: Optional[str] = UNDEFINED,
            # s3_endpoint_url: Optional[str] = UNDEFINED,
            # s3_region: Optional[str] = UNDEFINED,

            # Apenas para azure block blob backend:
            # azureblockblob_container_name: str = UNDEFINED,
            # azureblockblob_base_path: str = UNDEFINED,
            # azureblockblob_retry_initial_backoff_sec: float = UNDEFINED,
            # azureblockblob_retry_increment_base: float = UNDEFINED,
            # azureblockblob_retry_max_attempts: int = UNDEFINED,
            # azureblockblob_connection_timeout: float = UNDEFINED,
            # azureblockblob_read_timeout: float = UNDEFINED,

            # Apenas para elasticsearch backend:
            # elasticsearch_retry_on_timeout: bool = UNDEFINED,
            # elasticsearch_max_retries: int = UNDEFINED,
            # elasticsearch_timeout: float = UNDEFINED,
            # elasticsearch_save_meta_as_text: bool = UNDEFINED,

            # Apenas para AWS DynamoDB backend:
            # dynamodb_endpoint_url: Optional[str] = UNDEFINED,

            # Apenas para couchbase backend:
            # couchbase_backend_settings: Mapping = UNDEFINED,

            # Apenas para arangodb backend:
            # arangodb_backend_settings: Mapping = UNDEFINED,

            # Apenas para CosmosDB backend:
            # cosmosdbsql_database_name: str = UNDEFINED,
            # cosmosdbsql_collection_name: str = UNDEFINED,
            # cosmosdbsql_consistency_level: Literal[
            #     'Strong',
            #     'BoundedStaleness',
            #     'Session',
            #     'ConsistentPrefix',
            #     'Eventual',
            # ] = UNDEFINED,
            # cosmosdbsql_max_retry_attempts: int = UNDEFINED,
            # cosmosdbsql_max_retry_wait_time: float = UNDEFINED,
    ):
        """

        :param accept_content:
            Determina uma *white-list* dos serializers
            permitidos para processamento das mensagens por parte dos workers.
            Pode conter, por ex., "json", "pickle", "yaml", entre outros.
            O valor padrão do Celery é `{"json"}`.

        :param beat_schedule:
            Define tarefas periódicas (como cron jobs) que devem ser executadas
            em horários específicos ou em intervalos regulares usando o celery
            beat.
            O valor padrão do Celery é `{}`.

        :param broker_url:
            Contém a URL do broker que o Celery utilizará para enviar e
            receber mensagens de tarefas.
            O valor padrão do Celery é `"amqp://"`.

        :param database_engine_options:
            Apenas para database backend (db+).
            Permite especificar parâmetros adicionais usados por bancos
            que suportam `"SQLAlchemy"`.
            O valor padrão do Celery é `{}`.

        :param database_short_lived_sessions:
            Apenas para database backend (db+).
            Quando `True`, pode drasticamente reduzir performance do *backend*,
            principalmente em sistemas que processam muitas tarefas, mas podem
            ser úteis em sistemas com pouco tráfego de mensagens que
            experienciam erros resultados de conexões de banco cacheadas
            que acabam ficando inativas.
            O valor padrão do Celery é `False`.

        :param database_table_names:
            Apenas para database backend (db+).
            O Celery automaticamente criará duas tabelas para armazenar
            metadados das tarefas; Essa configuração permite personalizar o
            nome das tabelas.
            O valor padrão do Celery é `{}`.

        :param database_table_schemas:
            Apenas para database backend (db+).
            O Celery automaticamente criará duas tabelas para armazenar
            metadados das tarefas; Essa configuração permite personalizar o
            esquema das tabelas.
            O valor padrão do Celery é `{}`.

        :param enable_utc:
            Quando True, datas/horas contidas nas mensagens serão forçadas a
            usar o timezone UTC.
            O valor padrão do Celery é `True`.

        :param imports:
            Especifica uma lista de módulos que contêm as definições das
            tarefas do Celery.
            O valor padrão do Celery é `[]` (Nenhum módulo de tarefas é
            importado automaticamente).

        :param override_backends:
            Correlaciona um tipo de backend com o caminho até uma classe
            responsável por sobrescrever a implementação do backend.
            O valor padrão do Celery é `None`.

        :param result_accept_content:
            Similar ao argumento "`accept_content`", determina uma *white-list*
            dos serializers permitidos para o *result backend*.
            Quando `None`, utiliza o mesmo que o valor definido em
            "`accept_content`".
            O valor padrão do Celery é `None`.

        :param result_backend:
            Determina o `backend` usado para armazenar os resultados das
            tarefas.
            Devem começar com:
                - rpc: Envia os resultados de volta como mensagens AMQP;
                - database: Utiliza um banco relacional suportado por `"SQLAlchemy"`;
                - redis: Utiliza Redis para armazenar os resultados;
                - cache: Utiliza Memcached para armazenar os resultados;
                - mongodb: Utiliza MongoDB para armazenar os resultados;
                - cassandra: Utiliza Cassandra para armazenar os resultados;
                - elasticsearch: Utiliza Elasticsearch para armazenar os resultados;
                - ironcache: Utiliza IronCache para armazenar os resultados;
                - couchbase: Utiliza Couchbase para armazenar os resultados;
                - arangodb: Utiliza ArangoDB para armazenar os resultados;
                - couchdb: Utiliza CouchDB para armazenar os resultados;
                - filesystem: Utiliza um diretório compartilhado para armazenar os resultados;
                - consul: Utiliza `Consul K/V store` para armazenar os resultados;
                - azureblockblob: Utiliza `AzureBlockBlob PaaS store` para armazenar os resultados;
                - s3: Utiliza `S3` para armazenar os resultados;
            O valor padrão do Celery é `None`.

        :param result_backend_always_retry:
            Quando `True`, o `backend` sempre tentará novamente salvar os
            resultados, em casos de exceções recuperáveis, ao invés de propagar
            a exceção, até um máximo de duas tentativas (reduzindo o tempo
            entre cada tentativa).
            O valor padrão do Celery é `False`.

        :param result_backend_base_sleep_between_retries_ms:
            Determina o tempo base de espera entre as duas tentativas
            quando `result_backend_always_retry` for `True`.
            O valor padrão do Celery é `10`.

        :param result_backend_max_sleep_between_retries_ms:
            Determina o tempo máximo de espera entre as duas tentativas
            quando `result_backend_always_retry` for `True`.
            O valor padrão do Celery é `10000`.

        :param result_backend_max_retries:
            Determina o número máximo de tentativas quando
            `result_backend_always_retry` for `True`.
            O valor padrão do Celery é `2`.

        :param result_backend_transport_options:
            Mapping contendo opções adicionais para serem passadas para o
            transporte (Varia de acordo com o transporte sendo utilizado).
            O valor padrão do Celery é `{}`.

        :param result_cache_max:
            Determina a quantidade máxima de resultados em cache.
            Quando -1, desabilita o cache de resultados.
            Quando 0, determina que não há quantidade máxima.
            O valor padrão do Celery é `-1`.

        :param result_chord_join_timeout:
            Determina o tempo máximo (em segundos) que o *chord* irá aguardar
            os resultados das tarefas do grupo antes de dar *timeout*
            Se os resultados, de todas as tarefas do grupo, não estiverem todos
            disponíveis até o *timeout*, o *chord callback* será ativado
            apenas com as respostas disponíveis.
            O valor padrão do Celery é `3.0`.

        :param result_chord_retry_interval:
            Determina o intervalo de tempo (em segundos) entre as tentativas
            quando um *chord callback* dá *timeout* e ainda possui tarefas
            com resultado não-disponível - neste caso, ele aguarda o tempo
            informado antes de checar novamente.
            O valor padrão do Celery é `1.0`.

        :param result_compression:
            Determina o tipo de compressão usada nos resultados das tarefas.
            Os exemplos mais comuns são "gzip", "bzip2", "zlib".
            Quando `None`, não comprime as mensagens.
            O valor padrão do Celery é `None`.

        :param result_expires:
            Define o tempo de expiração (em segundos) (ou timedelta) dos
            resultados das tarefas armazenados. Após esse período, estes
            resultados serão removidos do backend de resultados.
            Quando None, significa que os resultados não serão automaticamente
            removidos.
            Não funciona com determinados tipos de *backend*.
            O valor padrão do Celery é `None`.

        :param result_extended:
            Quando `True`, permite escrever os atributos extras das tarefas
            (name, args, kwargs, worker, retries, queue, delivery_info)
            ao `backend`.
            O valor padrão do Celery é `False`.

        :param result_persistent:
            Apenas para rpc backend.
            Quando `True`, indica que os resultados seja persistentes, ou seja,
            não serão perdidos caso o *broker* reinicie (**OBS**: Corre o risco
            de levantar `celery.backends.rpc.BacklogLimitExceeded`).
            O valor padrão do Celery é `False`.

        :param result_serializer:
            Define o serializador a ser usado para serializar os resultados
            das tarefas antes de armazená-los.
            O valor padrão do Celery é `"json"` (Desde a versão 4.x+).

        :param task_acks_late:
            Quando `True`, determina que as tarefas devem ser confirmadas
            (*acknowledged*) somente após a conclusão bem-sucedida.
            O valor padrão do Celery é `False`.

        :param task_acks_on_failure_or_timeout:
            Quando `True`, determina que as tarefas serão confirmadas
            (*acknowledged*) mesmo se ocorrer erros ou *timeouts*.
            Só funciona caso `task_acks_late` seja `True`.
            O valor padrão do Celery é `True`.

        :param task_always_eager:
            Quando `True`, determina que as tarefas serão executadas localmente
            ao invés de serem enviadas para a fila.
            O valor padrão do Celery é `False`.

        :param task_annotations:
            Permite sobrescrever qualquer atributo de tarefas, como
            "rate_limit", *event hooks* (ex. on_failure), etc.
            Ao informar objetos como parâmetro, os mesmos deverão conter o
            método `annotate(self, task)`.
            O valor padrão do Celery é `None`.

        :param task_compression:
            Determina o tipo de compressão usada em mensagens de tarefas.
            Os exemplos mais comuns são "gzip", "bzip2", "zlib".
            Quando `None`, não comprime as mensagens.
            O valor padrão do Celery é `None`.

        :param task_default_queue:
            Determina o nome da fila padrão, usada pelo `.apply_async` caso
            a tarefa não esteja previamente roteada ou nenhuma fila tenha sido
            explicitamente informada.
            O valor padrão do Celery é `"celery"`.

        :param task_default_rate_limit:
            Determina um intervalo mínimo de tempo entre a execução de cada
            tarefa, aplicado em todas as tarefas.
            Pode ser um valor flutuante, representando os segundos, ou uma
            string com formato "<numero>/<tempo>", como por exemplo "10/s"
            (10 tarefas por segundo), "60/m" (60 tarefas por minuto), "100/h"
            (100 tarefas por hora) ou "1000/d" (1000 tarefas por dia), etc.
            O valor padrão do Celery é `None`.

        :param task_eager_propagates:
            Quando `True`, determina que as tarefas executadas localmente
            deverão propagar exceções.
            Equivale a rodar tarefas utilizando o método `.apply(throw=True)`.
            O valor padrão do Celery é `False`.

        :param task_ignore_result:
            Quando `True`, determina que os resultados das tarefas devem ser
            ignorados e descartados, não estando disponíveis para consulta
            posteriormente.
            Caso queira armazenar apenas erros, utilize o parâmetro
            `task_store_errors_even_if_ignored`.
            O valor padrão do Celery é `False`.

        :param task_protocol:
            Determina a versão do protocolo usado para enviar as tarefas.
            O valor padrão do Celery é `2` (Desde a versão 4.x+).

        :param task_publish_retry:
            Determina se o celery deverá utilizar a política de tentar
            novamente enfileirar mensagens que não puderam ser enfileiradas
            devido a erros diversos, como por exemplo de conectividade.
            O valor padrão do Celery é `True`.

        :param task_publish_retry_policy:
            Determina a política de tentativa de reenfileiramento das
            mensagens, somente em casos de mensagens que devam ser
            reenfileiradas.
            O valor padrão do Celery é `TaskPublishRetryPolicy()`.

        :param task_queues:


        :param task_reject_on_worker_lost:
            Mesmo que `task_acks_late` seja `True`, o worker irá confirmar
            (*acknowledge*) a tarefa caso seja concluído abruptamente ou
            sinalizado (ex. SIGKILL).
            Quando `True`, determina que as mensagens sejam reenfileiradas
            ao invés de confirmadas.
            O valor padrão do Celery é `False`.

        :param task_remote_tracebacks:
            Quando `True`, determina que os workers deverão incluir informação
            completa de *traceback* ao reportar erros para o nó principal.
            Não é recomendável deixar essa opção como `True` em ambiente de
            produção.
            Requer a lib `tblib` para usar o valor `True`.
            O valor padrão do Celery é `False`.

        :param task_serializer:
            Define o serializador a ser usado para serializar/deserializar
            as mensagens.
            Pode ser "json", "pickle", "yaml" ou "msgpack".
            Na teoria, pode ser criado um personalizado, mas todas as
            tentativas resultaram no worker dando 'exit code 0'.
            O valor padrão do Celery é `"json"`.

        :param task_soft_time_limit:
            Similar ao `task_time_limit`, porém determina um tempo limite
            para levantar a exceção `celery.exceptions.SoftTimeLimitExceeded`.
            Neste caso, o worker não é eliminado e haverá a possibilidade do
            worker de realizar alguma ação antes de atingir o tempo limite, por
            exemplo.
            O valor padrão do Celery é `None`.

        :param task_store_eager_result:
            Quando `True` e `task_alawys_eager` for `True` e
            `task_ignore_result` for `False`, os resultados de tarefas
            executadas localmente serão armazenadas no *backend*.
            O valor padrão do Celery é `False`.

        :param task_store_errors_even_if_ignored:
            Quando `True`, os workers irão armazenar todos os erros das tarefas,
            independente do parâmetro `task_ignore_result`.
            O valor padrão do Celery é `False`.

        :param task_time_limit:
            Tempo limite (em segundos) para a execução de uma tarefa.
            Caso o tempo seja excedido, o worker processando a tarefa será
            eliminado e substituído por um novo.
            Quando `None`, não possui tempo limite.
            O valor padrão do Celery é `None`.

        :param task_track_started:
            Quando `True`, a tarefa vai reportar o status "`STARTED`" quando
            for executada por um worker, provendo a capacidade de monitorar
            quais tarefas estão sendo executadas naquele instante, porém
            pode causar impacto na performance em caso de muitas tarefas curtas.
            Aparentemente não é necessário para o uso do `flower`.
            O valor padrão do Celery é `False`.

        :param timezone:
            Define o fuso horário padrão usado pelo Celery, que pode ser
            utilizado para agendar tarefas com base em horários específicos,
            por exemplo.
            O valor padrão do Celery é `"UTC"`.

        :param worker_cancel_long_running_tasks_on_connection_loss:
            Quando `True`, o worker cancelará automaticamente tarefas que estão
            em execução por um longo período de tempo quando a conexão com o
            *broker* for perdida (Evita que tarefas longas continuem sendo
            executadas se o worker não puder se comunicar com o broker, o
            que poderia resultar em tarefas sendo executadas mais de uma vez
            em algumas situações de falha).
            O valor padrão do Celery é `False` (`True` a partir da versão 6.x+).

        :param worker_enable_remote_control:
            Quando `True`, o worker permite que comandos sejam enviados a ele
            de forma remota, por exemplo, através do celery CLI ou de outros
            meios de controle remoto suportados pelo Celery, como o Flower.
            O valor padrão do Celery é `True`.

        :param worker_hijack_root_logger:
            Quando `True`, o worker substitui o logger raiz padrão pelo seu
            próprio logger, que é configurado internamente pelo Celery.
            O valor padrão do Celery é `True`.

        :param worker_max_tasks_per_child:
            Define o número máximo de tarefas que um processo do worker pode
            executar antes de ser substituído por um novo processo.
            Isso ajuda a evitar vazamentos de memória e outros problemas
            relacionados à execução prolongada de tarefas em um único processo.
            Quando `None`, indica que não há limite máximo.
            O valor padrão do Celery é `None`.

        :param worker_prefetch_multiplier:
            Define a quantidade de mensagens que o worker irá buscar do
            *broker* em cada iteração. Um valor maior pode melhorar o
            desempenho ao lidar com muitas mensagens pequenas, mas também pode
            levar a uma maior utilização de memória, pois as mensagens são
            mantidas em cache pelo worker.
            O valor padrão do Celery é `4`.

        """
        super().__init__(**self._serialize(vars()))

    @classmethod
    def _serialize(cls, o):
        if isinstance(o, dict):
            return {
                cls._serialize(k): cls._serialize(v)
                for k, v in o.items()
                if k != 'self' and not k.startswith('_') and v != UNDEFINED
            }
        elif isinstance(o, (list, set, tuple)):
            return type(o)(cls._serialize(v) for v in o)
        elif isinstance(o, (TaskRoute, QueueRoute)):
            return str(o)
        return o
