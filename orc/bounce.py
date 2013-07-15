from pippi import dsp
from pippi import tune
import math

shortname   = 'bo'
name        = 'bounce'
device      = 'default'
loop        = True

def play(args):
    length = dsp.stf(0.2)
    volume = 0.2 
    octave = 2 
    notes = ['d', 'a']
    quality = tune.major
    waveform = 'sine'
    ratios = tune.terry

    wtypes = ['sine', 'phasor', 'line', 'saw']

    for arg in args:
        a = arg.split(':')

        if a[0] == 't':
            length = dsp.stf(float(a[1]))

        if a[0] == 'v':
            volume = float(a[1]) / 100.0

        if a[0] == 'o':
            octave = int(a[1])

        if a[0] == 'n':
            notes = a[1].split('.')

        if a[0] == 'q':
            if a[1] == 'M':
                quality = tune.major
            elif a[1] == 'm':
                quality = tune.minor
            else:
                quality = tune.major

        if a[0] == 'tr':
            ratios = getattr(tune, a[1], tune.terry)

    harm = range(1, 12)

    layers = []
    for note in notes:
        freq = tune.ntf(note, octave, ratios) 
        #tonic = dsp.env(dsp.amp(dsp.tone(length, freq, 'sine2pi'), 0.2), 'phasor') * 500

        tones = []

        for t in range(4):
            angles = dsp.breakpoint([ freq * dsp.randchoose(harm) for f in range(dsp.randint(2, 20)) ], 100)
            angles = [ dsp.env(dsp.tone(length, a, 'sine2pi'), 'sine', amp=0.2) for a in angles ]
            tones += [ ''.join(angles) ]

        #layer = dsp.benv(dsp.mix(tones), [ dsp.rand(0.1, 0.7) for i in range(dsp.randint(5, 30)) ]) 
        layers += [ dsp.mix(tones) ]
        #layers += [ dsp.mix([layer, tonic]) ]
        #layers += [ layer ]

    out = dsp.mix(layers)

    return dsp.amp(out, volume)

