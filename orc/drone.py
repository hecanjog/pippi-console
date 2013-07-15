from pippi import dsp
from pippi import tune
import math

shortname   = 'dr'
name        = 'drone'
#device      = 'T6_pair3'
device      = 'default'
loop        = True

def play(params=None):
    params = params or {}

    length = params.get('length', dsp.stf(20))
    volume = params.get('volume', 20.0) 
    volume = volume / 100.0 # TODO move into param filter
    octave = params.get('octave', 1)
    notes = params.get('note', ['c', 'g'])
    hertz = params.get('hertz', False)
    quality = params.get('quality', tune.major)
    glitch = params.get('glitch', False)
    waveform = params.get('waveform', 'sine')
    ratios = params.get('ratios', tune.terry)
    alias = params.get('alias', False)
    wild = params.get('wii', False)
    bend = params.get('bend', False)
    bbend = params.get('bbend', False)
    env = params.get('envelope', 'gauss')
    harmonics = params.get('harmonic', [1,2])
    reps      = params.get('repeats', 1)
    root = params.get('root', 27.5)
    pinecone = params.get('pinecone', False)

    if bbend == True:
        bend = True

    tune.a0 = float(root)

    # These are amplitude envelopes for each partial,
    # randomly selected for each. Not to be confused with 
    # the master 'env' param which is the amplit
    wtypes = ['sine', 'phasor', 'line', 'saw']    
    layers = []

    if hertz is not False:
        notes = hertz

    for note in notes:
        tones = []
        for i in range(dsp.randint(2,4)):
            if hertz is not False:
                freq = float(note)

                if octave > 1:
                    freq *= octave
            else:
                freq = tune.ntf(note, octave)

            snds = [ dsp.tone(length, freq * h, waveform, 0.05) for h in harmonics ]
            snds = [ dsp.env(s, dsp.randchoose(wtypes), highval=dsp.rand(0.2, 0.4)) for s in snds ]
            snds = [ dsp.pan(s, dsp.rand()) for s in snds ]

            if bend is not False:
                def bendit(out=''):
                    if bbend == True:
                        bendtable = dsp.randchoose(['impulse', 'sine', 'line', 'phasor', 'cos', 'impulse'])
                        lowbend = dsp.rand(0.8, 0.99)
                        highbend = dsp.rand(1.0, 1.25)
                    else:
                        bendtable = 'sine'
                        lowbend = 0.99
                        highbend = 1.01

                    out = dsp.split(out, 441)

                    freqs = dsp.wavetable(bendtable, len(out))

                    freqs = [ math.fabs(f) * (highbend - lowbend) + lowbend for f in freqs ]

                    out = [ dsp.transpose(out[i], freqs[i]) for i in range(len(out)) ]
                    return ''.join(out)

                snds = [ bendit(snd) for snd in snds ]

            tones += [ dsp.mix(snds) ]

        layer = dsp.mix(tones)

        if wild != False:
            layer = dsp.vsplit(layer, 41, 4410)
            layer = [ dsp.amp(dsp.amp(l, dsp.rand(10, 20)), 0.5) for l in layer ]
            layer = ''.join(layer)
        
        if pinecone != False:
            layer = dsp.pine(layer, length, freq, 4)

        layer = dsp.env(layer, env)

        layers += [ layer ]

    out = dsp.mix(layers) * reps

    # Format is: [ path, offset, id, value ]
    if hertz is not False:
        osc_message = ['/dac', 0.0, 0, tune.fts(notes[0])]
    else:
        osc_message = ['/dac', 0.0, 0, tune.nts(notes[0], octave - 1)]

    #return (dsp.amp(out, volume), {'osc': [ osc_message ]})
    return dsp.amp(out, volume)
