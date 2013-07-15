from pippi import dsp
import math

shortname   = 'cl'
name        = 'click'
#device      = 'T6_pair3'
device      = 'default'
loop        = True

def play(params):

    length = params.get('length', dsp.stf(2))
    volume = params.get('volume', 100.0)
    volume = volume / 100.0 # TODO: move into param filter
    width = params.get('width', 50)
    measures = params.get('multiple', 1)
    beats = params.get('repeats', 8)
    bpm = params.get('bpm', 75.0)
    glitch = params.get('glitch', False)
    alias = params.get('alias', False)
    skitter = params.get('skitter', False)
    bend = params.get('bend', False)
    tweet = params.get('tweet', False)
    pattern = params.get('pattern', True)
    playdrums = params.get('drum', ['k', 'h', 'c'])
    pinecone = params.get('pinecone', False)
    insamp = params.get('rec', False)
    roll = params.get('roll', False)
    pi = params.get('pi', False)

    def bln(length, low=3000.0, high=7100.0, wform='sine2pi'):
        """ Time-domain band-limited noise generator
        """
        outlen = 0
        cycles = ''
        while outlen < length:
            cycle = dsp.cycle(dsp.rand(low, high), wform)
            outlen += len(cycle)
            cycles += cycle

        return cycles

    def eu(length, numpulses):
        pulses = [ 1 for pulse in range(numpulses) ]
        pauses = [ 0 for pause in range(length - numpulses) ]

        position = 0
        while len(pauses) > 0:
            try:
                index = pulses.index(1, position)
                pulses.insert(index + 1, pauses.pop(0))
                position = index + 1
            except ValueError:
                position = 0

        return pulses

    def getevents(lenbeat, pattern):
        """ Takes pattern: [0, 1]
            Returns event list: [[0, 44100], [1, 44100]]
        """

        events = []
        count = 0
        value = None
        event = []

        for p in pattern:

            prev = value
            value = p

            # Null to zero always starts new zero
            if prev is None and value is 0:
                # Start zero, add to length
                event = [0, lenbeat]

            # Any transition to one always starts new one
            elif value is 1:
                # Add last event if not empty to events and start a new one
                if len(event) == 2:
                    events += [ event ]

                # Start one, add to length
                event = [1, lenbeat]

            # One to zero always adds to one
            # Zero to zero always adds to zero
            elif prev is 0 or prev is 1 and value is 0:
                # Add to length
                event[1] += lenbeat

        return events

    def clap(amp, length):
        # Two layers of noise: lowmid and high
        out = dsp.mix([ bln(int(length * 0.2), 600, 1200), bln(int(length * 0.2), 7000, 9000) ])
        
        out = dsp.env(out, 'phasor')
        out = dsp.pad(out, 0, length - dsp.flen(out))

        return out

    def hihat(amp, length):
        def hat(length):
            if dsp.randint(0, 6) == 0:
                out = bln(length, 9000, 14000)
                out = dsp.env(out, 'line')
            else:
                out = bln(int(length * 0.05), 9000, 14000)
                out = dsp.env(out, 'phasor')
                out = dsp.pad(out, 0, length - dsp.flen(out))

            return out

        if dsp.randint() == 0:
            out = ''.join([ hat(length / 2), hat(length / 2) ])
        else:
            out = hat(length)

        return out

    def snare(amp, length):
        # Two layers of noise: lowmid and high
        out = dsp.mix([ bln(int(length * 0.2), 700, 3200, 'impulse'), bln(int(length * 0.01), 7000, 9000) ])
        
        out = dsp.env(out, 'phasor')
        out = dsp.pad(out, 0, length - dsp.flen(out))

        return out

    def kick(amp, length):
        fhigh = 160.0
        flow = 60.0
        fdelta = fhigh - flow

        target = length
        pos = 0
        fpos = fhigh

        out = ''
        while pos < target:
            # Add single cycle
            # Decrease pitch by amount relative to cycle len
            cycle = dsp.cycle(fpos)
            #cycle = ''.join([ str(v) for v in dsp.curve(0, dsp.htf(fpos), math.pi * 2) ])
            pos += dsp.flen(cycle)
            #fpos = fpos - (fhigh * (length / dsp.htf(fpos)))
            fpos = fpos - 30.0
            out += cycle

        return dsp.env(out, 'phasor')

    beats = beats * measures

    drums = [{
        'name': 'clap',
        'shortname': 'c',
        'trigger_id': 5,
        'gen': clap,
        'pat': eu(beats, dsp.randint(1, beats / 3)),
        }, {
        'name': 'hihat',
        'shortname': 'h',
        'trigger_id': 3,
        'gen': hihat,
        'pat': eu(beats, dsp.randint(1, beats / 3)),
        }, {
        'name': 'snare',
        'shortname': 's',
        'trigger_id': 4,
        'gen': snare,
        'pat': eu(beats, dsp.randint(1, beats / 2)),
        }, {
        'name': 'kick',
        'shortname': 'k',
        'trigger_id': 2,
        'gen': kick,
        'pat': eu(beats, dsp.randint(1, beats / 3)),
        }]

    out = ''
    lenbeat = dsp.mstf(60000.0 / bpm) / 4
    layers = []
    streams = []

    for drum in drums:
        if drum['shortname'] in playdrums:
            events = getevents(lenbeat, drum['pat'])
            layers += [ ''.join([ drum['gen'](event[0], event[1]) for event in events ]) ]

            if drum['shortname'] == 's':
                osc_messages = [ ['/tick', dsp.fts(lenbeat), drum['trigger_id'], int(h)] for h in drum['pat'] ]
            #stream = []
            #for h in drum['pat']:
                #stream += [ ('/tick/' + str(drum['trigger_id']), int(h), dsp.fts(lenbeat)) ]

            #streams += [ stream ]

    out = dsp.mix(layers)

    if bend is True:
        out = dsp.drift(out, dsp.rand(0.1, 2))

    if alias is True:
        out = dsp.alias(out)


    if glitch == True:
        out = dsp.split(out, int(lenbeat * 0.5))
        out = ''.join(dsp.randshuffle(out))

    if pi:
        return (dsp.amp(out, volume), {'osc': osc_messages })
    else:
        return dsp.amp(out, volume)

