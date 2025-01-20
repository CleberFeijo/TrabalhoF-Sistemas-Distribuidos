"""Módulo contendo as configurações de projeto."""

__all__ = 'project_settings',


class ProjectSettings:
    NOME: str = 'Template FastAPI + Celery'
    "Nome do projeto."

    VERSAO: str = '1.0.0'
    "Versão atual do projeto. Deve acompanhar as alterações em ``CHANGELOG.md``."


project_settings = ProjectSettings()
"""Singleton contendo as configurações padrões do projeto."""
