from server_info import ServerInfo

labels = {
    "LC1S": ("Time(s)", "Force (N)"),
    "LC_MAINS": ("Time(s)", "Force (N)"),
    "LC2S": ("Time(s)", "Force (N)"),
    "LC3S": ("Time(s)", "Force (N)"),
    "PT_FEEDS": ("Time(s)", "Pressure (PSI)"),
    "PT_COMBS": ("Time(s)", "Pressure (PSI)"),
    "PT_INJES": ("Time(s)", "Pressure (PSI)"),
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
    'TC1': ServerInfo.TC1S,
    'TC2': ServerInfo.TC2S,
    'TC3': ServerInfo.TC3S
}

data_lengths = {
    "LC1S": 1000,
    "LC_MAINS": 1000,
    "LC2S": 1000,
    "LC3S": 1000,
    "PT_FEEDS": 100,
    "PT_COMBS": 100,
    "PT_INJES": 100,
    "TC1S": 10,
    "TC2S": 10,
    "TC3S": 10,
}
