import re
from pippi import dsp
import os
import json
import pkgutil
from dumptruck import DumpTruck

patterns = {
        'millisecond':  re.compile(r'^ms\d+\.?\d*|\d+\.?\d*ms$'), 
        'second':       re.compile(r'^s\d+\.?\d*|\d+\.?\d*s$'), 
        'frame':        re.compile(r'^f\d+|\d+f$'), 
        'beat':         re.compile(r'^b\d+\.?\d*|\d+\.?\d*b$'), 
        'float':        re.compile(r'\d+\.?\d*'), 
        'integer':      re.compile(r'\d+'), 

        'hz':         re.compile(r'\d+\.?\d*hz$'), 
        'note':         re.compile(r'[a-gA-G][#b]?'), 
        'alphanumeric':      re.compile(r'\w+'), 
        'integer-list':      re.compile(r'\d+(.\d+)*'), 
        'note-list':      re.compile(r'[a-gA-G][#b]?(.[a-gA-G][#b]?)*'), 
        'hz-list':      re.compile(r'\d+\-?\d*?(.\d+\.?\d*)*'), 
        'string-list':      re.compile(r'[a-zA-Z]+(.[a-zA-Z]+)*'), 
        }

def get_session():
    return DumpTruck('session.db')

def import_types():
    # Load json config
    # Save types in session
    config_path = os.getcwd() + os.sep

    try:
        # Load from existing config if present
        with open(config_path + 'types.json', 'r+b') as configfile:
            config = json.load(configfile)

    except IOError:
        # Use global defaults
        config = pkgutil.get_data('pippic', 'data/types.json')
        config = json.loads(config)

        print 'Using global types. Create a types.json to override'

    s = get_session()

    for shortname, type in config.iteritems():
        type['shortname'] = shortname
        s.insert(type, 'types')

    return True

def get_generator(shortname):
    s = get_session()

    sql = "select * from generators where shortname = ?"
    generator = s.execute(sql, (shortname,))

    generator = False if generator == [] else generator[0]

    return generator

def get_type(shortname):
    s = get_session()

    sql = "select * from types where shortname = ?"
    type = s.execute(sql, (shortname,))

    if type == []:
        type = {
                'shortname': shortname, 
                'name': shortname,
                'accepts': None
            }
    else:
        type = type[0]

    return type

def get_type_or_generator(shortname=None):
    # Is this a generator?
    generator = get_generator(shortname)

    if generator == False:
        type = get_type(shortname)
    else:
        type = get_type('generator')
        type['generator_shortname'] = generator['shortname']
        type['generator_name'] = generator['name']

    return type

def is_type(value, flag):
    return patterns[flag].search(str(value))

def convert(value, input_type, output_type):
    # This is a dumb way to do this. Rehearsal approaches though...
    if input_type == 'string-list':
        return convert_string_list(value, output_type)

    if input_type == 'integer-list':
        return convert_integer_list(value, output_type)

    if input_type == 'integer': 
        return convert_integer(value, output_type)

    if input_type == 'float':
        return convert_float(value, output_type)

    if input_type == 'beat':
        return convert_beat(value, output_type)

    if input_type == 'second':
        return convert_second(value, output_type)

    if input_type == 'millisecond':
        return convert_millisecond(value, output_type)

    if input_type == 'note':
        return value

    if input_type == 'note-list':
        return convert_note_list(value, output_type)

    if input_type == 'hz-list':
        return convert_hz_list(value, output_type)

    if input_type == 'alphanumeric':
        return value


def convert_float(value, output_type='float'):
    value = patterns['float'].search(str(value)).group(0)

    if output_type == 'float':
        value = float(value)
    elif output_type == 'integer' or output_type == 'frame':
        value = int(float(value)) 
    elif output_type == 'integer-list':
        value = [int(float(value))]

    return value


def convert_integer(value, output_type='integer'):
    value = patterns['integer'].search(value).group(0)

    if output_type == 'float':
        value = float(value)
    elif output_type == 'integer' or output_type == 'frame':
        value = int(float(value)) 
    elif output_type == 'integer-list':
        value = [int(float(value))]

    return value

def convert_beat(value, output_type):
    value = patterns['float'].search(value).group(0)
    if output_type == 'frame':
        bpm = settings.config('bpm')
        value = dsp.bpm2ms(bpm) / float(value)
        value = dsp.mstf(value)

    return value 

def convert_millisecond(value, output_type):
    if output_type == 'frame':
        value = convert_float(value)
        value = dsp.mstf(value)

    return value 

def convert_second(value, output_type):
    if output_type == 'frame':
        value = convert_float(value)
        value = dsp.stf(value)

    return value 

def convert_hz_list(value, output_type):
    if output_type == 'hz-list':
        value = value.split('/')

    for i, hz in enumerate(value):
        value[i] = convert_float(hz)
    
    return value

def convert_note_list(value, output_type):
    if output_type == 'note-list':
        value = value.split('.')
    
    return value

def convert_string_list(value, output_type):
    if output_type == 'string-list':
        value = value.split('.')
        value = [str(v) for v in value]

    return value

def convert_integer_list(value, output_type):
    if output_type == 'integer-list':
        value = value.split('.')
        value = [int(v) for v in value]

    return value


