import os
import json
from pprint import pprint
from dumptruck import DumpTruck
import subprocess
from pippic import types
from pippi import dsp
import pkgutil

session_filename = 'session.db'

def init_config():
    """ Loads a pippi.json config file if exists at root of 
    current working directory, otherwise creates a new config 
    with defaults.
    """

    config_path = os.getcwd() + os.sep + 'pippi.config'

    try:
        # Load from existing config if present
        with open(config_path, 'r+b') as configfile:
            config = json.load(configfile)

    except IOError:
        exit('No valid config file found')

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
    #cmd = "sqlite3 %s < default.sql" % session_filename
    #with open(os.devnull, 'w') as dev_null:
    #    subprocess.call(cmd, shell=True, stdout=dev_null)

    # Populate config table with json data
    s = get_session()

    s.insert([ {"name": name, "value": value } for name, value in config.iteritems() ], "config")

    # Load types
    types.import_types()

def new_session(dirname):
    """ Creates a basic pippi session from scratch in a new directory.
        
        Structure:

        dirname/            # From supplied name
            readme.md       # Quick start instructions
            orc/            # Dir for pippi generators
                example.py  # Example generator
            pippi.json      # Example config
            .gitignore      # Example gitignore with common pippi settings

    """

    here = os.getcwd()

    projdir = here + os.sep + dirname

    if os.path.exists(projdir):
        exit('Oops, that directory exists already.')

    # Create the directory
    os.mkdir(projdir)

    # Drop in the default readme
    with open(projdir + os.sep + 'readme.md', 'wb') as readme:
        content = pkgutil.get_data('pippic', 'data/readme.md')
        readme.write(content)

    # Create orc directory for generators
    os.mkdir(projdir + os.sep + 'orc')

    # Add an example generator script
    with open(projdir + os.sep + 'orc' + os.sep + 'example.py', 'wb') as generator:
        content = pkgutil.get_data('pippic', 'data/orc_example.py')
        generator.write(content)

    # Create sounds directory for ...sounds
    os.mkdir(projdir + os.sep + 'sounds')

    # Create default config file
    with open(projdir + os.sep + 'pippi.config', 'wb') as generator:
        content = pkgutil.get_data('pippic', 'data/config.json')
        generator.write(content)

    # Add example .gitignore file
    with open(projdir + os.sep + '.gitignore', 'wb') as gitignore:
        content = pkgutil.get_data('pippic', 'data/gitignore.default')
        gitignore.write(content)

def import_generators(generators):
    s = get_session()

    for i, g in generators.iteritems():
        generator = {
                'shortname': g.shortname,
                'name': g.name
                }

        s.insert(generator, 'generators')

    return True

def config(key, value=None):
    s = get_session()

    if value is not None:
        # Set the value
        sql = "update config set value = ? where name = ?"
        s.execute(sql, (value, key))
    else:
        # Get the value
        sql = "select value from config where name = ?"
        value = s.execute(sql, (key,))
        if value == []:
            return None
        else:
            value = value[0]['value']

    return value

def shared(key, value=None):
    s = get_session()

    if value is not None:
        # Set the value
        s.insert({'name': key, 'value': value}, 'shared', upsert=True)
    else:
        # Get the value
        sql = "select value from shared where name = ?"
        try:
            value = s.execute(sql, (key,))[0]['value']
        except IndexError:
            value = 0 # Prolly gonna reget this. TODO - betterer?

    return value


def buffer(voice_id, value=None):
    if value is not None:
        dsp.write(value, 'cache/buf-%s' % voice_id)
    else:
        value = dsp.read('cache/buf-%s.wav' % voice_id).data

    return value

def get_param(voice_id, key, default=None):
    try:
        return param(voice_id, key)
    except IndexError:
        return default

def param(voice_id, key, value=None, gen=None, default=None):
    s = get_session()

    if voice_id == 'all' and gen is None:
        sql = "update params set value = ? where name = ?"
        s.execute(sql, (value, key))

        return value

    elif voice_id == 'all' and gen is not None:
        sql = "update params set value = ? where name = ? and generator = ?"
        s.execute(sql, (value, key, gen))

        return value

    if value is not None:
        # Set the value
        sql = "update params set value = ? where name = ? and voice_id = ?"
        s.execute(sql, (value, key, voice_id))
    else:
        # Get the value
        sql = "select output_type, value from params where name = ? and voice_id = ?"
        p = s.execute(sql, (key, voice_id))[0]

        value = p['value']

        if p['output_type'] == 'integer':
            value = int(value)

        elif p['output_type'] == 'float':
            value = float(value)

    return value

def get_all_params():
    voices = get_voices()

    voice_params = []

    for voice in voices:
        voice_params += [ { 'voice': voice, 'params': get_params(voice['id']) } ]

    return voice_params

def get_voices():
    s = get_session()

    sql = "select * from voices order by id"
    return s.execute(sql)

def get_params(voice_id):
    s = get_session()

    sql = "select name, value from params where voice_id = ?"
    return s.execute(sql, (voice_id,))

def voice(voice_id, key, value=None):
    s = get_session()

    if voice_id == 'all' and value is not None:
        sql = "update voices set %s = ?" % key
        s.execute(sql, (value,))

        return value

    elif voice_id == 'all' and gen is not None:
        sql = "update params set value = ? where name = ? and generator = ?"
        s.execute(sql, (value, key, gen))

        return value

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

    sql = "delete from params where voice_id = ?"
    s.execute(sql, (voice_id,))

def parse_cmds(cmds, voice_id=None):
    """ Parse a raw command string typed at the pippi console or 
        sent by a robot friend and return a list of param dicts in 
        db/session format. (See default schema for canonical format)
        """
    cmds = cmds.strip().split(' ')
    params = [ parse_cmd(cmd, voice_id) for cmd in cmds ]

    vparams = [ p[0] for p in params if p[1] == True ]
    params = [ p[0] for p in params if p[1] == False ]

    generator = [ p for p in params if p['name'] == 'generator' ]

    return generator, vparams, params 

def parse_cmd(cmd, voice_id=None):
    """ Parse a single command and 
        return a param dict.
    """

    # Names for reserved voice metadata
    vp = ['re', 'once', 'uno', 'qu']

    # Raw param commands are given in the format 
    #   key:value
    # or for booleans just 
    #   key
    cmd = cmd.split(':')

    # Determine names and types
    shortname = cmd[0]
    type = types.get_type_or_generator(shortname=shortname)

    name = type['name']
    accepts = type['accepts']
    output_type = type['output_type']

    value = cmd[1] if len(cmd) == 2 else True

    if value == 'F':
        value = False

    if name == 'generator':
        value = type['generator_shortname']

    if accepts is not None:
        for input_type in accepts:
            if types.is_type(value, input_type):
                cooked = types.convert(value, input_type, output_type)
                break
            else:
                cooked = False
    elif name == 'generator':
        cooked = type['generator_name']
    else:
        cooked = value

    param = {
            'name': name,
            'shortname': shortname,
            'accepts': accepts,
            'output_type': output_type,
            'value': value,
            'cooked': cooked,
            'voice_id': voice_id
        }

    return param, param['shortname'] in vp


def add_voice(cmds):
    s = get_session()

    generator, vparams, params = parse_cmds(cmds)

    def searchp(params, pname, default):
        for index, p in enumerate(params):
            if p['shortname'] == pname:            
                return p['cooked']

        return default 

    # Check for missing required params and insert defaults
    voice = {
            'loop': True, 
            'regenerate': searchp(vparams, 're', False), 
            'once': searchp(vparams, 'once', False), 
            'uno': searchp(vparams, 'uno', False), 
            'quantize': searchp(vparams, 'qu', False), 
            'target_volume': 1.0, 
            'post_volume': 1.0,
            'generator': generator[0]['cooked']
        }

    voice_id = s.insert(voice, 'voices')

    for i, p in enumerate(params):
        params[i]['voice_id'] = voice_id

    # TODO: device, root, a0, bpm, other config values, etc
    # Names for globally present params (insert if not specified)
    gp = { 
            'bpm': 'bpm', 
            'device': 'device'
    }

    for shortname, longname in gp.iteritems():
        dvalue = config(shortname)

        cmd = '%s:%s' % (shortname, dvalue)

        p = parse_cmd(cmd, voice_id)
        params += [ p[0] ]
    
    s.insert(params, 'params')

    return voice_id, generator[0]['value']

def get_session(session_filename='session.db'):
    return DumpTruck(session_filename)

