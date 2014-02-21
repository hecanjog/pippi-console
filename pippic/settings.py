import os
import json
from pprint import pprint

default_session_name = os.getcwd().split(os.sep)[-1]
default_config = {
        "name": default_session_name,
        "shortname": default_session_name[:3],
        "session": "pippi.session",
        "bpm": 80.0,
        "a0": 27.5,
        "root": "b",
        "quality": "major",
        "tune": "terry",
        "paths": {
            "orc": "orc/",
            "sounds": "sounds/",
            "snapshots": "snapshots/"
        }
    }

def init_config():
    """ Loads a pippi.json config file if exists at root of 
    current working directory, otherwise creates a new config 
    with defaults.

    Then updates current session with config params if not already 
    present in the session database.
    """

    try:
        # Load from existing config if present
        print 'Loading config settings into session...'
        with open(os.getcwd() + os.sep + 'pippi.json', 'r+b') as configfile:
            config = json.load(configfile)

    except IOError:
        # Create new config from defaults
        print 'Creating default config file...'
        with open(os.getcwd() + os.sep + 'pippi.json', 'wb') as configfile:
            json.dump(default_config, configfile, indent=4, separators=(', ', ': '))
            config = default_config

    # Load config data into current session - default behavior is overwrite...?

    return config
