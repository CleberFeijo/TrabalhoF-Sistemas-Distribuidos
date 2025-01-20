"""Arquivo contendo as configurações do serviço do flower."""
log_level = 'DEBUG'
persistent = True
purge_offline_workers = 24 * 60 * 60
state_save_interval = 5000
