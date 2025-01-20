from copy import deepcopy
from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.middleware import Middleware
from fastapi.routing import APIRoute, BaseRoute
from inspect import signature
from starlette.types import Lifespan

from common.classes import ModuleIterator, UNDEFINED
from common.enums import EnvEnum
from common.typealiases import (
    Any,
    Callable,
    Coroutine,
    Mapping,
    ModuleT,
    Sequence,
    Type,
)

from .classes import ServerOptions
from .exception_handlers import map_exception_handlers
from .functions import generate_unique_id, run_server

__all__ = 'App',


class App:
    """
    Classe auxiliar responsável por armazenar os dados de instanciação
    da aplicação FastAPI, bem como suas subaplicações e rotas extendidas de
    `APIRouter`.

    A instância de FastAPI é criada apenas uma única vez ao acessar a property
    `self.app`, montando as subaplicações e incluindo as respectivas rotas.
    """

    module_defaults = {
        'docs_url': '/docs/swagger/',
        'exception_handlers': map_exception_handlers(),
        'generate_unique_id_function': generate_unique_id,
        'redoc_url': '/docs/redoc/',
    }

    inheritable_kwargs = (
        'exception_handlers',
        'generate_unique_id_function',
    )

    # Extende os decorators de criação de rotas do FastAPI.
    @property
    def get(self):
        return self.app.get

    @property
    def put(self):
        return self.app.put

    @property
    def post(self):
        return self.app.post

    @property
    def delete(self):
        return self.app.delete

    @property
    def options(self):
        return self.app.options

    @property
    def head(self):
        return self.app.head

    @property
    def patch(self):
        return self.app.patch

    @property
    def trace(self):
        return self.app.trace

    # noinspection PyUnusedLocal
    # OBS: valores são acessados através do vars()
    def __init__(
            self,
            path: str | None = UNDEFINED,
            name: str | None = UNDEFINED,
            *,
            use_defaults: bool = UNDEFINED,
            routers: ModuleT | Sequence[APIRouter] | None = UNDEFINED,
            subapps: ModuleT | Sequence['App'] | None = UNDEFINED,
            server_options: dict[EnvEnum, ServerOptions] | ServerOptions | None = UNDEFINED,

            # kwargs padrão do FastAPI.
            callbacks: list[BaseRoute] | None = UNDEFINED,
            contact: dict[str, Any] | None = UNDEFINED,
            debug: bool = UNDEFINED,
            default_response_class: Type[Response] = UNDEFINED,
            dependencies: Sequence[Depends] | None = UNDEFINED,
            deprecated: bool | None = UNDEFINED,
            description: str = UNDEFINED,
            docs_url: str | None = UNDEFINED,
            exception_handlers: dict[
                int | Type[Exception],
                Callable[[Request, Any], Coroutine[Any, Any, Response]],
            ] | None = UNDEFINED,
            generate_unique_id_function: Callable[[APIRoute], str] = UNDEFINED,
            include_in_schema: bool = UNDEFINED,
            license_info: dict[str, Any] | None = UNDEFINED,
            middleware: Sequence[Middleware] | None = UNDEFINED,
            on_shutdown: Sequence[Callable[[], Any]] | None = UNDEFINED,
            on_startup: Sequence[Callable[[], Any]] | None = UNDEFINED,
            lifespan: Lifespan[FastAPI] | None = UNDEFINED,
            openapi_prefix: str = UNDEFINED,
            openapi_tags: list[dict[str, Any]] | None = UNDEFINED,
            openapi_url: str | None = UNDEFINED,
            redoc_url: str | None = UNDEFINED,
            responses: dict[int | str, dict[str, Any]] | None = UNDEFINED,
            root_path: str = UNDEFINED,
            root_path_in_servers: bool = UNDEFINED,
            routes: list[BaseRoute] | None = UNDEFINED,
            servers: list[dict[str, Any]] | None = UNDEFINED,
            swagger_ui_init_oauth: dict[str, Any] | None = UNDEFINED,
            swagger_ui_oauth2_redirect_url: str | None = UNDEFINED,
            swagger_ui_parameters: dict[str, Any] | None = UNDEFINED,
            terms_of_service: str | None = UNDEFINED,
            title: str = UNDEFINED,
            version: str = UNDEFINED,
            **kwargs: Any,
    ):
        self._app: FastAPI = None
        self.parent: 'App' = None
        self.name = name
        self.path = path
        self.use_defaults = use_defaults
        self.server_options = server_options
        self.routers = self._routers_to_list(routers)
        self.subapps = self._subapps_to_list(subapps)

        self.kwargs = {
            k: v
            for k, v in vars().items()
            if k in signature(FastAPI.__init__).parameters and k != 'self'
        }
        self.kwargs.update(kwargs)

    @property
    def app(self) -> FastAPI:
        if not self._app:
            self._app = FastAPI(**self.get_init_kwargs())

            for subapp in self.subapps:
                subapp.parent = self
                if not subapp.name or not subapp.path:
                    raise ValueError(
                        'Subaplicações, obrigatoriamente, devem conter os '
                        'campos "name" e "path" informados.'
                    )
                self._app.mount(path=subapp.path, name=subapp.name, app=subapp.app)

            for router in self.routers:
                self._app.include_router(router)

        return self._app

    @property
    def should_use_defaults(self) -> bool:
        if isinstance(self.use_defaults, bool):
            return self.use_defaults
        if self.parent:
            return self.parent.should_use_defaults
        return False

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    def get_init_kwargs(self):
        kwargs = deepcopy(self.kwargs)

        if self.parent:
            parent_kwargs = self.parent.get_init_kwargs()

            for k in self.inheritable_kwargs:
                if kwargs.get(k, UNDEFINED) == UNDEFINED:
                    kwargs[k] = parent_kwargs.get(k, UNDEFINED)

        if self.should_use_defaults:
            for k, v in self.module_defaults.items():
                if kwargs.get(k, UNDEFINED) == UNDEFINED:
                    kwargs[k] = v

        return {k: v for k, v in kwargs.items() if v != UNDEFINED}

    def run_server(self, app_path: str):
        if isinstance(self.server_options, Mapping):
            from core.settings import env
            run_server(app=self.app, app_path=app_path, options=self.server_options[env])
        elif isinstance(self.server_options, ServerOptions):
            run_server(app=self.app, app_path=app_path, options=self.server_options)

        raise NotImplementedError('Não há configurações de inicialização do '
                                  'servidor.')

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    def _subapps_to_list(self, subapps: Any):
        subapps_list = []
        if isinstance(subapps, ModuleT):
            subapps_list.extend(ModuleIterator(subapps).it_instances(self.__class__))
        elif isinstance(subapps, Sequence):
            for s in subapps:
                subapps_list.extend(self._subapps_to_list(s))
        elif isinstance(subapps, self.__class__):
            subapps_list.append(subapps)
        return subapps_list

    def _routers_to_list(self, routers: Any):
        routers_list = []
        if isinstance(routers, ModuleT):
            routers_list.extend(ModuleIterator(routers).it_instances(APIRouter))
        elif isinstance(routers, Sequence):
            for r in routers:
                routers_list.extend(self._routers_to_list(r))
        elif isinstance(routers, APIRouter):
            routers_list.append(routers)
        return routers_list
