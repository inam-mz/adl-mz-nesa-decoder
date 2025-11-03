from adl_ftp_plugin.registries import ftp_decoder_registry
from django.apps import AppConfig


class NESAMZPluginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "adl_mz_nesa_decoder"
    
    def ready(self):
        from .decoders import NESAMZDecoder
        
        ftp_decoder_registry.register(NESAMZDecoder())
