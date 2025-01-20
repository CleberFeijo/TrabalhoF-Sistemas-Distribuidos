# Cria um "stage" com determinada versão do python3;
FROM python:3.10.14 AS default_stage

# Define o diretório de trabalho;
ARG workdir
WORKDIR $workdir

# Instala pacotes e serviços;
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

# Atualiza o pip e instala os requerimentos;
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --default-timeout=100 -r requirements.txt && \
    rm -f requirements.txt

# Seta algumas variáveis de ambiente do python e timezone;
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ="America/Sao_Paulo"

# Adiciona os arquivos do "Sources Root" ao projeto;
COPY ./src ./


# Cria o "stage" dos workers celery.
FROM default_stage AS worker_stage

# Remove os arquivos/diretórios que não serão utilizados pelos workers celery;
RUN rm -rf app tests .flake8 pytest.ini
