from pippi import dsp

shortname       = 'sl'
name            = 'slurp'
#device          = 'T6_pair2'
device      = 'default'
loop            = True

def play(params={}):
    volume = params.get('volume', 100.0)
    volume = volume / 100.0 # TODO: move into param filter
    volume = volume * 0.25
    length = params.get('length', 40)
    env    = params.get('envelope', False)
    wii    = params.get('wii', False)
    speed  = params.get('speed', False)
    
    numcycles = dsp.randint(10, 524)

    # Make breakpoint env with 2-10 vals between 0.1 and 1.0
    curve_a = dsp.breakpoint([1.0] + [dsp.rand(0.1, 1.0) for r in range(dsp.randint(2, 10))] + [0], numcycles)

    # Make wavetable with single cycle from given wave types
    curve_types = ['vary', 'phasor', 'sine', 'cos', 'impulse']
    curve_b = dsp.wavetable(dsp.randchoose(curve_types), numcycles)

    # Make pan curve - always cosine
    pan = dsp.wavetable('cos', numcycles)

    # Multiply breakpoint curve with simple wavetable
    wtable = [ curve_a[i] * curve_b[i] for i in range(numcycles) ]

    # Scale to max frequency
    wtable = [ (f * 19000) + length for f in wtable ]

    # Possible osc wavetypes
    wtypes = ['impulse', 'tri', 'cos', 'sine2pi', 'vary']

    if wii is True:
        out = [ dsp.pan(dsp.cycle(wtable[i], dsp.randchoose(wtypes)), pan[i]) for i in range(numcycles) ]
    else:
        wtype = dsp.randchoose(wtypes)
        out = [ dsp.pan(dsp.cycle(wtable[i], wtype), pan[i]) for i in range(numcycles) ]

    out = dsp.amp(''.join(out), volume)

    if speed != False and speed > 0.0:
        out = dsp.transpose(out, speed)

    if env != False:
        out = dsp.env(out, env)

    return out

