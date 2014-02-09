from pippi import dsp
from pippi import tune

shortname   = 'pp'
name        = 'pulsar'
#device      = 'T6_pair1'
device      = 'default'
loop        = True

def play(params):
    length      = params.get('length', dsp.mstf(dsp.rand(10, 1000)))
    #length      = params.get('length', dsp.mstf(200))
    volume      = params.get('volume', dsp.rand(70.0, 100.0)) / 100.0

    note        = params.get('note', ['c'])[0]
    root        = params.get('root', 27.5)
    bpm         = params.get('bpm', 75.0)

    env         = params.get('envelope', 'random')
    mod         = params.get('mod', 'random')
    modFreq     = params.get('modfreq', 1.0 / dsp.fts(length))
    modRange    = params.get('modrange', dsp.rand(0, 0.05))
    pulsewidth  = params.get('pulsewidth', dsp.rand(0.01, 0.8))
    window      = params.get('window', 'random')
    waveform    = params.get('waveform', 'random')
    waveform    = params.get('waveform', 'tri')

    padding     = params.get('padding', dsp.randint(0, 4410 * 3))
    padding     = 0

    #freq = tune.fromdegrees([1], root='c')
    freq        = params.get('freq', dsp.rand(165, 168))
    #freq *= 2**dsp.randint(0, 4)

    freq        = params.get('freq', 220.0)

    freq *= dsp.rand(0.15, 4.1)

    tune.a0 = float(root)

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    out = dsp.pulsar(freq, length, pulsewidth, waveform, window, mod, modRange, modFreq, volume)

    try:
        out = dsp.env(out, env)
    except TypeError:
        out = dsp.env(out, 'sine')

    out = dsp.pad(out, 0, padding)

    out = dsp.pan(out, dsp.rand())

    return out

