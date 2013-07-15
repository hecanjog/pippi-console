from pippi import dsp
import math

shortname       = 'sw'
name            = 'sweep'
#device          = 'T6_pair1'
device      = 'default'
loop            = True

def play(params):
    pinecone = params.get('pinecone', False)
    wild = params.get('wild', False)
    pad = params.get('pad', False)
    high = params.get('high', True)
    up = params.get('up', False)
    long = params.get('long', False)
    wide = params.get('wide', False)

    layers = []

    if long == True:
        numgrains = dsp.randint(8000, 20000)
    else:
        numgrains = dsp.randint(10, 1000)

    def dosweep(wtype, start_freq, freq_range, numgrains, cycle_type):
        out = ''
        pitch_curve = dsp.curve(wtype, numgrains, math.pi * 0.5, freq_range, 0.0, start_freq)
        pan_curve = dsp.curve(1, numgrains, math.pi * dsp.rand(1, 80))
        for i, freq in enumerate(pitch_curve):
            grain = dsp.cycle(freq, cycle_type, 0.01)
            grain = dsp.pan(grain, pan_curve[i])
            out += grain

        return out

    wtype = 2 if up == True else 1

    if wild == True:
        cycle_types = ['sine', 'impulse', 'vary', 'tri']    
        cycle_type = dsp.randchoose(cycle_types)
    else:
        cycle_type = 'sine'

    numsweeps = dsp.randint(1, 10)
    for i in range(numsweeps):
        if high == True:
            start_freq = dsp.rand(1000, 19000)
        else:
            start_freq = dsp.rand(50, 1000)

        if wide == True:
            freq_range = dsp.rand(500, 1000)
        else:
            freq_range = dsp.rand(1, 50)

        layer = dosweep(wtype, start_freq, freq_range, numgrains, cycle_type)
        
        if pinecone == True:
            if wild == True:
                windows = [0, 1, 2, 6]
                window = dsp.randchoose(windows)
                scrubs = [0, 1, 2, 6]
                scrub = dsp.randchoose(scrubs)
            else:
                window = 2
                scrub = 5

            length = dsp.stf(dsp.rand(0.05, 1))
            layer = dsp.pine(layer, length, dsp.rand(50, 10000), window, dsp.rand(1, 10), scrub, dsp.rand(1, 10))

        layers += [ layer ]

    out = dsp.mix(layers)

    if pad == True:
        pad = dsp.stf(dsp.rand(0.01, 1))
        out = dsp.pad(out, 0, pad)

    env_types = ['hann', 'line','phasor', 'sine', 'impulse', 'vary', 'tri']    
    env_type = dsp.randchoose(env_types)

    out = dsp.env(out, env_type)

    return out
