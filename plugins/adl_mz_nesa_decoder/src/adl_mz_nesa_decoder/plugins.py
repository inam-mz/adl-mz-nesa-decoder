from adl.core.registries import Plugin


class NESAMZDecoderPlugin(Plugin):
    type = "adl_mz_nesa_decoder"
    label = "ADL MZ Nesa Decoder"
    
    def get_urls(self):
        return []
    
    def get_station_data(self, station_link, start_date=None, end_date=None):
        return []
