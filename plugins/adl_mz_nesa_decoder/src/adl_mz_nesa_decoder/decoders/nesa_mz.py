import logging

import pandas as pd
from adl_ftp_plugin.registries import FTPDecoder
from django.utils import timezone as dj_timezone

logger = logging.getLogger(__name__)


class NESAMZDecoder(FTPDecoder):
    type = "nesamz"
    compat_type = "nesamz"
    display_name = "NESAMZ FTP Decoder - Mozambique"
    
    def get_matching_files(self, station_link, files, start_date=None, end_date=None):
        # get all the initial matching files
        matching_files = super().get_matching_files(station_link, files, start_date=start_date, end_date=end_date)
        
        if station_link.start_date:
            return matching_files
        
        timezone = station_link.timezone
        
        # Only get files for today if no start_date specified
        zero_padded_day_today = [f"{dj_timezone.localtime(timezone=timezone).day:02}"]
        matching_files = [file for file in matching_files if any(date in file for date in zero_padded_day_today)]
        
        return matching_files
    
    def decode(self, file_path):
        """
        This method decodes the NESAMZ format.
        
        File format:
        S,RecordID,Hour,Min,Sec,Day,Month,Year,[ID1,ID2,Value triplets...],#
        
        Example:
        S,000011,15,00,00,25,09,2025,1,2,35.3,1,3,35.0,1,4,35.5,...,#
        
        :param file_path: The path to the file to decode.
        :return: A dictionary containing the decoded data.
        """
        
        records = []
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Remove start marker 'S,' and end marker '#'
                if line.startswith('S,'):
                    line = line[2:]
                if line.endswith('#'):
                    line = line[:-1]
                
                # Split the line by comma
                parts = line.split(',')
                
                if len(parts) < 8:
                    logger.warning(f"Skipping invalid line: {line}")
                    continue
                
                try:
                    # Parse header information
                    record_id = parts[0]
                    hour = int(parts[1])
                    minute = int(parts[2])
                    second = int(parts[3])
                    day = int(parts[4])
                    month = int(parts[5])
                    year = int(parts[6])
                    
                    # Create datetime
                    observation_time = pd.Timestamp(year=year, month=month, day=day,
                                                    hour=hour, minute=minute, second=second)
                    
                    # Parse triplets (ID1, ID2, Value)
                    data = {
                        'record_id': record_id,
                        'observation_time': observation_time
                    }
                    
                    # Process triplets starting from index 7
                    i = 7
                    while i + 2 < len(parts):
                        id1 = parts[i]
                        id2 = parts[i + 1]
                        value_str = parts[i + 2]
                        
                        # Create key
                        key = f"{id1};{id2}"
                        
                        # Convert value to float, handle errors
                        try:
                            value = float(value_str)
                        except ValueError:
                            logger.warning(f"Could not convert value '{value_str}' for key {key}")
                            value = None
                        
                        data[key] = value
                        
                        i += 3
                    
                    records.append(data)
                
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing line: {line}. Error: {e}")
                    continue
        
        return {
            "values": records
        }
