from common.typealiases import Iterator, ModuleT, Type, T

__all__ = 'ModuleIterator',


class ModuleIterator:
    """Classe contendo funções de iteração de módulos python."""

    def __init__(self, module: ModuleT):
        self.module = module

    # ====================== #
    # ~~~~| Properties |~~~~ #
    # ====================== #

    @property
    def module_dict(self):
        return self.module.__dict__

    @property
    def module_keys(self):
        return self.module_dict.keys()

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def it_classes(
            self,
            subclass_of: Type[T] = None,
            *,
            deep_search: bool = True,
            bypass_all_dunder: bool = False,
    ) -> Iterator[Type[T]]:
        """
        Itera sobre um módulo python, retornando apenas as classes encontradas
        neste módulo.

        - Não retorna classes privadas.

        :param subclass_of: Retorna apenas a classe (ou subclasses) do valor
            informado;
        :param deep_search: Quando True, também itera os submódulos;
        :param bypass_all_dunder: Quando True, ignora o atributo "__all__" dentro
                do módulo, iterando todas as instâncias, não só as definidas em
                "__all__".
        """
        for k in self._get_it_keys(bypass_all_dunder):
            try:
                v = self.module_dict[k]
            except KeyError:
                continue

            # Só retorna classes.
            if not isinstance(v, type):
                continue

            # Realiza a varredura de submódulos.
            if deep_search and isinstance(v, ModuleT):
                yield from ModuleIterator(v).it_classes(
                    subclass_of=subclass_of,
                    deep_search=deep_search,
                    bypass_all_dunder=bypass_all_dunder,
                )
                continue

            # Realiza a checagem de tipo.
            if subclass_of and not issubclass(v, subclass_of):
                continue

            # Retorna a classe.
            yield v

    def it_instances(
            self,
            instance_of: Type[T] = None,
            *,
            deep_search: bool = True,
            bypass_all_dunder: bool = False,
    ) -> Iterator[T]:
        """
        Itera sobre um módulo python, retornando os objetos encontrados
        neste módulo;

        - Não retorna instâncias privadas nem classes.

        :param instance_of: Retorna apenas as instâncias do tipo informado;
        :param deep_search: Quando True, também itera os submódulos;
        :param bypass_all_dunder: Quando True, ignora o atributo "__all__" dentro
                do módulo, iterando todas as instâncias, não só as definidas em
                "__all__".
        """
        for k in self._get_it_keys(bypass_all_dunder):
            try:
                v = self.module_dict[k]
            except KeyError:
                continue

            # Não retorna classes.
            if isinstance(v, type):
                continue

            # Realiza a varredura de submódulos.
            if deep_search and isinstance(v, ModuleT):
                yield from ModuleIterator(v).it_instances(
                    instance_of=instance_of,
                    deep_search=deep_search,
                    bypass_all_dunder=bypass_all_dunder,
                )
                continue

            # Realiza a checagem de tipo.
            if instance_of and not isinstance(v, instance_of):
                continue

            # Retorna a instância.
            yield v

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    def _get_it_keys(self, bypass_all_dunder: bool):
        """
        Retorna as chaves que deverão ser iteradas no módulo.

        - Elimina as chaves que começam com "_" (não itera atributos privados).

        :param bypass_all_dunder: Quando True, ignora o atributo "__all__" do
            módulo.
        :return:
        """
        if '__all__' not in self.module_dict or bypass_all_dunder:
            it_keys = self.module_keys
        else:
            it_keys = self.module_dict.get('__all__', [])

        yield from [k for k in it_keys if not k.startswith('_')]
