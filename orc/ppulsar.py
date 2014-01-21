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
    volume      = params.get('volume', dsp.rand(1.0, 80.0)) / 100.0

    note        = params.get('note', ['c'])[0]
    root        = params.get('root', 27.5)
    bpm         = params.get('bpm', 75.0)

    env         = params.get('envelope', 'random')
    mod         = params.get('mod', 'random')
    modFreq     = params.get('modfreq', 1.0 / dsp.fts(length))
    modRange    = params.get('modrange', dsp.rand(0, 0.5))
    pulsewidth  = params.get('pulsewidth', dsp.rand(0.01, 0.8))
    window      = params.get('window', 'random')
    waveform    = params.get('waveform', 'random')
    waveform    = params.get('waveform', 'vary')

    padding     = params.get('padding', dsp.randint(0, 4410 * 3))
    padding     = 0

    freq        = params.get('freq', dsp.rand(11, 300))
    #freq        = params.get('freq', 440.0)

    tune.a0 = float(root)

    mod = dsp.wavetable(mod, 512)
    window = dsp.wavetable(window, 512)
    waveform = dsp.wavetable(waveform, 512)

    out = dsp.pulsar(freq, length, pulsewidth, waveform, window, mod, modRange, modFreq, volume)

    out *= dsp.randint(1, 4)

    #if env == 'random':
        #env = dsp.randchoose(['line', 'phasor', 'vary', 'hann', 'sine'])

    #print dsp.flen(out)
    try:
        out = dsp.env(out, env)
    except TypeError:
        out = dsp.env(out, 'sine')

    out = dsp.pad(out, 0, padding)

    return out

