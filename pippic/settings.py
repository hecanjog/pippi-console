import os
import json
from pprint import pprint
from dumptruck import DumpTruck
import subprocess
from pippic import param
from pippi import dsp

session_filename = 'pippi.session'
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
        "orc": "orc/",
        "sounds": "sounds/",
        "snapshots": "snapshots/"
    }

def init_config():
    """ Loads a pippi.json config file if exists at root of 
    current working directory, otherwise creates a new config 
    with defaults.
    """

    config_path = os.getcwd() + os.sep + 'pippi.json'

    try:
        # Load from existing config if present
        with open(config_path, 'r+b') as configfile:
            config = json.load(configfile)

    except IOError:
        # Create new config from defaults
        print 'Creating default config file...'
        with open(config_path, 'wb') as configfile:
            json.dump(default_config, configfile, indent=4, separators=(', ', ': '))
            config = default_config

    return config

def init_session():
    """ Backs up existing session if one exists
        then starts a fresh one with data from pippi.json.
    """
    config = init_config()

    if os.path.isfile(session_filename):
        # Make a dump
        cmd = "sqlite3 %s .dump > %s.bak.sql" % (session_filename, session_filename)
        with open(os.devnull, 'w') as dev_null:
            subprocess.call(cmd, shell=True, stdout=dev_null)

        # Remove db
        os.remove(session_filename)
    
    # Create new db from default schema
    cmd = "sqlite3 %s < default.sql" % session_filename
    with open(os.devnull, 'w') as dev_null:
        subprocess.call(cmd, shell=True, stdout=dev_null)

    # Populate config table with json data
    s = get_session()

    s.insert([ {"name": name, "value": value } for name, value in config.iteritems() ], "config")

def config(key, value=None):
    s = get_session()

    if value is not None:
        # Set the value
        sql = "update config set value = ? where name = ?"
        s.execute(sql, (value, key))
    else:
        # Get the value
        sql = "select value from config where name = ?"
        value = s.execute(sql, (key,))[0]['value']

    return value

def buffer(voice_id, value=None):
    if value is not None:
        dsp.write(value, 'cache/buf-%s' % voice_id)
    else:
        value = dsp.read('cache/buf-%s.wav' % voice_id).data

    return value

def param(voice_id, key, value=None):
    s = get_session()

    if value is not None:
        # Set the value
        sql = "update params set value = ? where name = ? and voice_id = ?"
        s.execute(sql, (value, key, voice_id))
    else:
        # Get the value
        sql = "select value from params where name = ? and voice_id = ?"
        try:
            value = s.execute(sql, (key, voice_id))[0]['value']
        except IndexError:
            print value

    return value

def get_params(voice_id):
    s = get_session()

    print voice_id

    sql = "select * from params where voice_id = ?"
    params = s.execute(sql, (voice_id,))

    print params

    return params

def voice(voice_id, key, value=None):
    s = get_session()

    if value is not None:
        # Set the value
        sql = "update voices set %s = ? where id = ?" % key
        s.execute(sql, (value, voice_id))
    else:
        # Get the value
        sql = "select * from voices where id = ?"
        value = s.execute(sql, (voice_id,))[0][key]

    return value


def remove_voice(voice_id):
    s = get_session()

    sql = "delete from voices where id = ?"
    s.execute(sql, (voice_id,))

def add_voice(params):
    s = get_session()

    # Post-render params are still awkward
    if 'loop' in params.data:
        loop = True
        params.data.pop('loop')
    else:
        loop = False

    if 're' in params.data:
        regenerate = True
        params.data.pop('re')
    else:
        regenerate = False

    if 'once' in params.data:
        once = True
        params.data.pop('once')
    else:
        once = False

    if 'uno' in params.data:
        uno = True
        params.data.pop('uno')
    else:
        uno = False

    if 'quantize' in params.data:
        quantize = True
        params.data.pop('quantize')
    else:
        quantize = False

    voice = {'loop': loop, 'regenerate': regenerate, 'volume': 1.0, 'post_volume': 1.0}
    voice_id = s.insert(voice, 'voices')

    for p in params.data:
        output_type = params.types.get(p, {'name': p})
        if 'type' in output_type:
            output_type = output_type['type']
        else:
            output_type = 'boolean'

        cooked = params.get(p)
        value = params.data[p]['value']
        name = params.data[p]['name']
        shortname = p

        p = {
            'name': name,
            'shortname': shortname,
            'output_type': output_type,
            'value': value,
            'cooked': cooked,
            'voice_id': voice_id
        }

        s.insert(p, 'params')

    return voice_id


def get_session():
    s = DumpTruck(session_filename)
    s.connection.text_factory = str # Allows us to store byte strings
    return s

