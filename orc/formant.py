from pippi import dsp
from pippi import tune
import math

shortname   = 'fo'
name        = 'formant'
device      = 'default'
loop        = True

def play(args):
    length = dsp.stf(30)
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

    harm = range(1, 30)
    layers = []
    for note in notes:
        tones = []
        freq = tune.ntf(note, octave, ratios) 

        for i in range(30):
            angles = dsp.breakpoint([freq * dsp.randchoose(harm) for f in range(dsp.randint(3, 50))], dsp.randint(350, 500))
            alen = int(length / len(angles)) * 2

            angles = [ dsp.env(dsp.tone(alen, a, 'random'), 'sine') for a in angles ]

            # Each overtone blip should overlap by about 50% with its neighbor...
            lowangles = ''.join([ angle for i, angle in enumerate(angles) if i % 2 == 0 ])

            highangles = [ angle for i, angle in enumerate(angles) if i % 2 != 0 ]
            highangles[0] = dsp.cut(highangles[0], dsp.flen(highangles[0]) / 2, dsp.flen(highangles[0]) / 2)
            highangles = ''.join(highangles)

            tones += [ dsp.benv(dsp.amp(dsp.mix([lowangles, highangles]), 0.9), [dsp.rand(0.1, 0.9) for i in range(dsp.randint(5, 30))]) ]

        tones = dsp.mix(tones)
        #tonic = dsp.env(dsp.amp(dsp.tone(int(length * 0.6), freq, 'sine2pi'), 0.1), 'flat')

        #layers += [ dsp.mix([tones, tonic], False) ]
        layers += [ tones ]

    out = dsp.mix(layers)

    return dsp.amp(out, volume)

if __name__ == '__main__':
    print dsp.write(play([]), 'weeooo')
