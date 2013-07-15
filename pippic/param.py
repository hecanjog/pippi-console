import re
from pippi import dsp

class Param:
    types = {
            'o': {
                'name': 'octave',
                'type': 'integer',
                'accepts': ['integer', 'float'],
                },
            'm': {
                'name': 'multiple',
                'type': 'integer',
                'accepts': ['integer'],
                },
            'n': {
                'name': 'note',
                'type': 'note-list',
                'accepts': ['note-list'],
                },
            'hz': {
                'name': 'hertz',
                'type': 'hz-list',
                'accepts': ['hz-list'],
                },
            'h': {
                'name': 'harmonic',
                'type': 'integer-list',
                'accepts': ['integer-list'],
                },
            'e': {
                'name': 'envelope',
                'type': 'string',
                'accepts': ['alphanumeric'],
                },
            'wf': {
                'name': 'waveform',
                'type': 'string',
                'accepts': ['alphanumeric'],
                },
            'd': {
                'name': 'drum',
                'type': 'string-list',
                'accepts': ['string-list'],
                },
            'r': {
                'name': 'repeats',
                'type': 'integer',
                'accepts': ['integer'],
                },
            'i': {
                'name': 'instrument',
                'type': 'string',
                'accepts': ['alphanumeric'],
                },
            's': {
                'name': 'scale',
                'type': 'integer-list',
                'accepts': ['integer-list'],
                },
            'sp': {
                'name': 'speed',
                'type': 'float',
                'accepts': ['float', 'integer'],
                },
            't': {
                'name': 'length',
                'type': 'frame',
                'accepts': ['beat', 'second', 'millisecond', 'integer'],
                },
            'p': {
                'name': 'padding',
                'type': 'frame',
                'accepts': ['beat', 'second', 'millisecond', 'integer'],
                },

            'w': {
                'name': 'width',
                'type': 'frame',
                'accepts': ['integer', 'beat', 'millisecond', 'second'],
                },
            'tt': {
                'name': 'trigger_id',
                'type': 'integer',
                'accepts': ['integer'],
                },
            'v': {
                'name': 'volume',
                'type': 'float',
                'input_range': [0, 100],
                'output_range': [0.0, 1.0],
                'accepts': ['integer', 'float'],
                },
            're': {
                'name': 'regenerate',
                },
            'qu': {
                'name': 'quantize',
                },
            'a': {
                'name': 'alias',
                },
            'tw': {
                'name': 'tweet',
                },
            'be': {
                'name': 'bend',
                },
            'bpm': {
                'name': 'bpm',
                'type': 'float',
                'accepts': ['float', 'integer'],
                },
            'device': {
                    'name': 'device',
                    'type': 'string',
                    'accepts': ['alphanumeric'],
                },

            'generator': {
                    'name': 'generator',
                    'type': 'string',
                    'accepts': ['alphanumeric'],
                },

            }

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

    def __init__(self, data=None):
        """ Create an instance with key-value dict or list of key-value lists
        """
        if data is None:
            data = {}

        if hasattr(data, 'iteritems'):
            self.data = { param: { 'value': value } for (param, value) in data.iteritems() }
        elif hasattr(data, '__iter__'):
            self.data = {}
            for param in data:
                value = param[1] if len(param) == 2 else True
                self.data[param[0]] = {'value': value}

    def istype(self, value, flag):
        return self.patterns[flag].search(str(value))

    def convert(self, value, input_type, output_type):
        # This is a dumb way to do this. Rehearsal approaches though...
        if input_type == 'string-list':
            return self.convert_string_list(value, output_type)

        if input_type == 'integer-list':
            return self.convert_integer_list(value, output_type)

        if input_type == 'integer': 
            return self.convert_integer(value, output_type)

        if input_type == 'float':
            return self.convert_float(value, output_type)

        if input_type == 'beat':
            return self.convert_beat(value, output_type)

        if input_type == 'second':
            return self.convert_second(value, output_type)

        if input_type == 'millisecond':
            return self.convert_millisecond(value, output_type)

        if input_type == 'note':
            return value

        if input_type == 'note-list':
            return self.convert_note_list(value, output_type)

        if input_type == 'hz-list':
            return self.convert_hz_list(value, output_type)

        if input_type == 'alphanumeric':
            return value


    def convert_float(self, value, output_type='float'):
        value = self.patterns['float'].search(str(value)).group(0)

        if output_type == 'float':
            value = float(value)
        elif output_type == 'integer' or output_type == 'frame':
            value = int(float(value)) 
        elif output_type == 'integer-list':
            value = [int(float(value))]

        return value


    def convert_integer(self, value, output_type='integer'):
        value = self.patterns['integer'].search(value).group(0)

        if output_type == 'float':
            value = float(value)
        elif output_type == 'integer' or output_type == 'frame':
            value = int(float(value)) 
        elif output_type == 'integer-list':
            value = [int(float(value))]

        return value

    def convert_beat(self, value, output_type):
        value = self.patterns['float'].search(value).group(0)
        if output_type == 'frame':
            value = dsp.bpm2ms(self.data.get('bpm')['value']) / float(value)
            value = dsp.mstf(value)

        return value 

    def convert_millisecond(self, value, output_type):
        if output_type == 'frame':
            value = self.convert_float(value)
            value = dsp.mstf(value)

        return value 

    def convert_second(self, value, output_type):
        if output_type == 'frame':
            value = self.convert_float(value)
            value = dsp.stf(value)

        return value 

    def convert_hz_list(self, value, output_type):
        if output_type == 'hz-list':
            value = value.split('/')

        for i, hz in enumerate(value):
            value[i] = self.convert_float(hz)
        
        return value

    def convert_note_list(self, value, output_type):
        if output_type == 'note-list':
            value = value.split('.')
        
        return value

    def convert_string_list(self, value, output_type):
        if output_type == 'string-list':
            value = value.split('.')
            value = [str(v) for v in value]

        return value

    def convert_integer_list(self, value, output_type):
        if output_type == 'integer-list':
            value = value.split('.')
            value = [int(v) for v in value]

        return value

    def get(self, param_name, default=False):
        """ Get a param value by its key and 
            convert from an acceptable input type 
            to the specified output type.
            """
        # TODO: This whole thing has a stupid, convoluted flow. Fix.

        if param_name in self.data:
            param = self.data[param_name]
            if param_name not in self.types:
                return param.get('value', False)

            param.update(self.types[param_name])
        else:
            return default

        
        # Translate special R params into random ranges for certain params
        if hasattr(param['value'], '__getslice__') and param['value'][0] == 'R':
            # TODO make more robust
            if param_name == 'bpm':
                if len(param['value']) > 1:
                    param['value'] = param['value'][1:].split('.')
                    tmin = float(param['value'][0])
                    tmax = float(param['value'][1])

                else:
                    tmin = 100
                    tmax = 1000

                param['value'] = str(dsp.rand(tmin, tmax))

            #elif param_name == 't':
                ## Length rand range
                #if len(param['value']) > 1:
                    #param['value'] = param['value'][1:].split('.')
                    #tmin = int(param['value'][0])
                    #tmax = int(param['value'][1])

                #else:
                    #tmin = 100
                    #tmax = 1000

                #param['value'] = str(dsp.randint(tmin, tmax)) + 'ms'


            elif param_name == 's':
                # My favorite scale degrees
                param['value'] = '.'.join([ str(dsp.randint(1, 6)) for r in range(dsp.randint(2, 4)) ])
            elif param_name == 'o':
                # Octave rand range
                param['value'] = str(dsp.randint(1, 5))


        if 'accepts' in param and 'type' in param:
            # Loop through each acceptable input type
            # and check to see if param value matches
            # one of them. 
            for input_type in param['accepts']:
                if self.istype(param['value'], input_type):
                    # At the first match, convert param value to target type
                    # and break out of the loop.
                    param = self.convert(param['value'], input_type, param['type'])
                    break
            else:
                # Return false when input doesn't match any of the accepted types
                param = False

        elif 'value' in param and param['value'] is True:
            param = param['value']

        return param 

    def set(self, param_key, value):
        if param_key in self.data:
            param = self.data[param_key]
            param['value'] = value
            self.data[param_key] = param 
        else:
            if param_key in self.types:
                self.data[param_key] = self.types[param_key]
            else:
                self.data[param_key] = {}
            
            self.data[param_key]['value'] = value

    def collapse(self):
        data = {}

        for param in self.data:
            type = self.types.get(param, {'name': param})

            data[type['name']] = self.get(param)

        return data


def unpack(cmd, generators, params):
    """ Format an input string as an expanded dictionary based on 
        required configuration options.
        """

    params = Param() 

    # Split space-separated params into a list
    cmds = cmd.strip().split()

    # Split colon-separated key:value param pairs
    # into lists.
    cmds = [ cmd.split(':') for cmd in cmds ]

    # Try to find generator from the list of
    # registered generators for the session
    for cmd in cmds:
        # Look up the list of registered generators and try to expand
        # the shortname into the full generator name
        #if len(cmd) == 1 and cmd[0] in config['generators']:
        if len(cmd) == 1 and cmd[0] in config['generators']:
            params.data['generator'] = config['generators'][cmd[0]]

        # Look up the list of registered params and try to expand
        # the shortname into the full param name, leaving the value 
        # untouched. 
        elif len(cmd) == 2 and cmd[0] in config['params']:
            param = config['params'][cmd[0]]
            param['value'] = cmd[1]
            params.data[param['name']] = param

        elif len(cmd) == 1 and cmd[0] not in config['generators']:
            if cmd[0] in config['params']:
                param = config['params'][cmd[0]]
                if 'name' in param:
                    cmd[0] = param['name']

            params.data[cmd[0]] = { 'name': cmd[0], 'value': True }

    return params

