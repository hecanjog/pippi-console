from pippi import dsp
from pippi import tune

shortname   = 'sp'
name        = 'sparkle'
device      = 'default'
loop        = True

def play(params={}):

    length    = params.get('length', dsp.stf(20))
    volume    = params.get('volume', 0.3)
    octave    = params.get('octave', 6)
    note      = params.get('note', 'c')
    quality   = params.get('quality', tune.major)
    multiple  = params.get('multiple', 1)
    width     = params.get('width', 0)
    waveform  = params.get('waveform', 'vary')
    chirp     = params.get('chirp', False)
    harmonics = params.get('harmonics', [1, 2])
    scale     = params.get('scale', [1, 4, 6, 5, 8])
    wavetypes = params.get('wavetypes', ['sine', 'phasor', 'line', 'saw'])
    ratios    = params.get('ratios', tune.terry)
    glitch    = params.get('glitch', False)

    def chirp(s):
        length = dsp.flen(s)

        #chirps = [ dsp.chirp(dsp.randint(10, 10000), 60, 5000, dsp.randint(1,100)) for c in range(100) ]
        chirps = [ dsp.chirp(
                        numcycles=dsp.randint(50, 1000), 
                        lfreq=dsp.rand(9000, 12000), 
                        hfreq=dsp.rand(14000, 20000), 
                        length=441 + (i * 41),
                        etype=dsp.randchoose(['gauss', 'sine', 'line', 'phasor']),
                        wform=dsp.randchoose(['sine', 'tri', 'phasor', 'line'])) 
                    for i in range(100) ]
        chirps = [ dsp.pan(c, dsp.rand()) for c in chirps ]

        chirps = ''.join(chirps)

        return dsp.fill(chirps, length)

    tones = []
    multiple *= 1.0
    freqs = tune.fromdegrees(dsp.randshuffle(scale), octave, note[0])
    for i in range(dsp.randint(2,4)):
        #freq = tune.step(i, note, octave, dsp.randshuffle(scale), quality, ratios)
        freq = freqs[i % len(freqs)]

        snds = [ dsp.tone(length, freq * h, waveform) for h in harmonics ]
        for snd in snds:
            snd = dsp.vsplit(snd, dsp.mstf(10 * multiple), dsp.mstf(100 * multiple))
            if width != 0:
                for ii, s in enumerate(snd):
                    if width > dsp.mstf(5):
                        owidth = int(width * dsp.rand(0.5, 2.0))
                    else:
                        owidth = width

                    olen = dsp.flen(s)
                    s = dsp.cut(s, 0, owidth)
                    s = dsp.pad(s, 0, olen - dsp.flen(s)) 
                    snd[ii] = s

            snd = [ dsp.env(s, dsp.randchoose(wavetypes)) for s in snd ]
            snd = [ dsp.pan(s, dsp.rand()) for s in snd ]
            snd = [ dsp.amp(s, dsp.rand()) for s in snd ]
                
            if chirp == True:
                snd = [ chirp(s) for s in snd ]

            snd = ''.join(snd)

            tones += [ snd ]

    out = dsp.mix(tones)
    out = dsp.pan(out, 0)

    return dsp.amp(out, volume)
