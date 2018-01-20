from server_info import ServerInfo

labels = {
    "LC1S": ("Time(s)", "Force (N)"),
    "LC_MAIN": ("Time(s)", "Force (N)"),
    "LC2S": ("Time(s)", "Force (N)"),
    "LC3S": ("Time(s)", "Force (N)"),
    "PT_FEED": ("Time(s)", "Pressure (PSI)"),
    "PT_COMB": ("Time(s)", "Pressure (PSI)"),
    "PT_INJE": ("Time(s)", "Pressure (PSI)"),
    "TC1S": ("Time(s)", "Temperature (C)"),
    "TC2S":("Time(s)", "Temperature (C)"),
    "TC3S": ("Time(s)", "Temperature (C)"),
}

str_to_byte = {
    'LC1S': ServerInfo.LC1S,
    'LC_MAIN': ServerInfo.LC_MAINS,
    'LC2S': ServerInfo.LC2S,
    'LC3S': ServerInfo.LC3S,
    'PT_FEED': ServerInfo.PT_FEEDS,
    'PT_COMB': ServerInfo.PT_COMBS,
    'PT_INJE': ServerInfo.PT_INJES,
    'TC1S': ServerInfo.TC1S,
    'TC2S': ServerInfo.TC2S,
    'TC3S': ServerInfo.TC3S
}

#TODO update these values at some point
# Data lengths is how many total samples we want to keep for graphing
# e.g. 60000 at 1000 samples/second would be 1 minute of data
data_lengths = {
    "LC1S": 1000,
    "LC_MAIN": 1000,
    "LC2S": 1000,
    "LC3S": 1000,
    "PT_FEED": 100,
    "PT_COMB": 100,
    "PT_INJE": 100,
    "TC1S": 10,
    "TC2S": 10,
    "TC3S": 10,
}

# Samples to keep is how many samples we actually want to show in the graph
# See data_ratio in animate() in gui_final
samples_to_keep = {
    "LC1S": 250,
    "LC_MAIN": 500,
    "LC2S": 250,
    "LC3S": 250,
    "PT_FEED": 50,
    "PT_COMB": 50,
    "PT_INJE": 50,
    "TC1S": 10,
    "TC2S": 10,
    "TC3S": 10,
}
