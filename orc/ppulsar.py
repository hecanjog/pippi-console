from pippi import dsp
from pippi import tune

shortname   = 'pp'
name        = 'pulsar'
#device      = 'T6_pair1'
device      = 'default'
loop        = True

def play(params):
    volume      = params.get('volume', dsp.rand(70.0, 100.0)) / 100.0

    notes       = params.get('note', [ dsp.randchoose(['c', 'f', 'e', 'a', 'd']) for i in range(2) ])

    octave =    params.get('octave', dsp.randint(1, 5)) 

    root        = params.get('root', 27.5)
    bpm         = params.get('bpm', 75.0)

    if dsp.randint(0, 1) == 0:
        length      = params.get('length', dsp.mstf(dsp.rand(10, 2000)))
    else:
        length      = params.get('length', int(dsp.randint(1, 4) * dsp.bpm2frames(bpm) * 0.25))

    env         = params.get('envelope', 'random')
    env         = params.get('envelope', 'tri')
    mod         = params.get('mod', 'random')
    modFreq     = params.get('modfreq', dsp.rand(1.0, 1.5) / dsp.fts(length))
    modRange    = params.get('speed', 0.01)
    modRange    = dsp.rand(0, modRange)

    pulsewidth  = params.get('pulsewidth', dsp.rand(0.01, 0.8))
    window      = params.get('window', 'gauss')
    #waveform    = params.get('waveform', 'random')
    waveform    = params.get('waveform', 'tri')

    glitch    = params.get('glitch', True)

    pulsewidth = 1.0


    freqs   = [ tune.ntf(note, octave) for note in notes ]

    tune.a0 = float(root)

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    layers = []

    for freq in freqs:
        layers += [ dsp.pulsar(freq, length, pulsewidth, waveform, window, mod, modRange, modFreq, volume) ]

    out = dsp.mix(layers)

    try:
        out = dsp.env(out, env)
    except TypeError:
        out = dsp.env(out, 'sine')

    if glitch:
        bitlen = dsp.randint(dsp.mstf(10), dsp.mstf(500))
        bit = dsp.cut(out, dsp.randint(0, len(out) - bitlen), bitlen)
        out = dsp.vsplit(out, dsp.mstf(10), dsp.mstf(500))
        out.insert(dsp.randint(0, len(out) - 2), bit)

        out = ''.join(out)

    out = dsp.pan(out, dsp.rand())

    return out

