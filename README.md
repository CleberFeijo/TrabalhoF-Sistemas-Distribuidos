# Tipador v3
Projeto dedicado a servir de base para criação de outros projetos com utilização
do FastAPI.


## Configurações Iniciais

---

1. Clone este projeto;
2. Copie o arquivo `.env.template` como `.env` e preecha as variáveis de ambiente.
3. Se estiver usando `Pycharm`:
   - Marque o diretório `/src/` como *Sources Root*; 
     - Clique com o botão direito sobre o diretório;
     - Procure a opção `Mark Directory as` > `Sources Root`.
   - Defina a *docstring* como *reStructuredText*;
     - Vá em `Settings` (`CTRL+ALT+S`);
     - Procure `Tools` > `Python Integrated Tools`;
     - Vá em `Docstrings`, na primeira configuração `Docstring Format` selecione `reStructuredText`.  


## Estrutura
Descrição da estrutura do diretório `src/`.

---

- `/src/app/`
  - Módulo contendo a aplicação FastAPI, suas subaplicações, rotas,
    dependências e `hooks de eventos`.
- `/src/common/`
  - Diretório contendo classes, enums, funções e afins genéricos, que costumam
    ser amplamente utilizados em outros pacotes, e que normalmente não dependem
    de libs externas.
- `/src/core/`
  - Diretório contendo configurações e pré-definições utilizadas pelo projeto,
    como por exemplo loggers, enums, etc.
- `/src/logs/`
  - Diretório contendo os arquivos de logs de aplicações, como o GUnicorn, 
    workers celery, etc.
- `/src/mq/`
  - Diretório contendo as configurações do rabbitmq e celery, como as filas,
    tarefas agendadas, etc.
- `/src/tests/`
  - Diretório contendo os testes do pytest.
- `/src/utils/`
  - Diretório contendo pacotes complementares à libs específicas do python.


## Libs adicionais

---

### Flake8
https://flake8.pycqa.org/

- As configurações do flake8 se encontram no arquivo `.flake8`, no diretório
  "src" do projeto.
- Quando em ambiente de desenvolvimento, o flake8 roda automaticamente ao
  iniciar ao levantar o container `app`, mas também toda vez que é detectada
  alguma alteração no código.
- Também é possível rodar o flake8 manualmente através do seguinte comando:

```bash
make flake8
```


### Pytest
https://docs.pytest.org/en/7.1.x/

- As configurações do pytest se encontram no arquivo `pytest.ini`, no "src" do 
  projeto.
- Recomenda-se criar os testes dentro do módulo `/src/tests/` (`pytest.ini` já 
  vem pré-configurado para olhar este módulo quando buscar os testes).
 
Para realizar **TODOS** os testes unitários, suba o container `app` e utilize 
o seguinte comando:

```bash
make pytest
```

**OBS**: Rodar o teste com o comando sem "python3" (ou "python") poderá 
  acarretar em erro de importação de módulos.

**OBS 2**: Alguns testes unitários requerem que o container do mongodb local
  esteja levantado. O Makefile já está configurado para levantar esse container.
