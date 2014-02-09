from pippi import dsp
from pippic import rt
from pippi import tune
import os
import subprocess
import time

shortname       = 'in'
name            = 'ins'
device          = 'T6_pair3'
#device          = 'default'
loop            = True

def sox(cmd, sound):
    stamp = str(time.time())
    path = os.getcwd()
    filename_in = '/tmp/proc-in' + stamp
    filename_out = '/tmp/proc-out' + stamp + '.wav'

    dsp.write(sound, filename_in)

    cmd = cmd % (path + filename_in + '.wav', path + filename_out)
    subprocess.call(cmd, shell=True)

    sound = dsp.read(path + filename_out).data

    return sound


def play(params):
    length          = params.get('length', dsp.mstf(10000))
    buffer_index    = params.get('buffer_index', False)
    sample_index    = params.get('sample_index', False)
    buffer_length   = params.get('buffer_length', dsp.stf(5))
    volume          = params.get('volume', 100.0) / 100.0
    scale           = params.get('scale', [25, 50, 100, 200])
    octave          = params.get('octave', 0)
    envelope        = params.get('envelope', False)
    glitch          = params.get('glitch', True)
    overdub         = params.get('dub', False)
    pad             = params.get('padding', False)
    pan             = params.get('pan', False)

    if sample_index != False:
        out = dsp.read('samps/pre/buf-%s.wav' % str(sample_index)).data
    elif buffer_index != False:
        fname = 'samps/buf-%s' % str(buffer_index)

        if not os.path.exists(fname + '.wav') or overdub == True:
            out = rt.capture(buffer_length, 'T6_pair1', 1)
            out = sox("sox %s %s silence 1 0.1 1%% -1 0.1 1%%", out)
            out = dsp.transpose(out, 0.5)
        else:
            out = dsp.read('samps/buf-%s.wav' % str(buffer_index)).data
    else:
        out = rt.capture(buffer_length, 'T6_pair1', 1)
        out = sox("sox %s %s silence 1 0.1 1%% -1 0.1 1%%", out)
        out = dsp.transpose(out, 0.5)

    speeds = [ s / 100.0 for s in scale ]
    #speeds = [ 0.25, 0.5, 1.0, 2.0 ]

    if glitch == True:
        grain_length = dsp.flen(out) / 4 

        out = dsp.vsplit(out, int(grain_length * 0.5), grain_length)
        numgrains = (length / grain_length) * 2

        if len(out) < numgrains:
            for i in range(numgrains - len(out)):
                out += [ dsp.randchoose(out) ]

        layers = []

        for index in range(1, 20):
            layer = dsp.randshuffle(out)

            if pad is not False:
                layer = [ dsp.pad(grain, 0, pad) for grain in layer ]

            layer = [ dsp.env(grain, 'sine') for grain in layer ]
            layer = [ dsp.transpose(grain, dsp.randchoose(speeds) * 2**octave * 0.25) for grain in layer ]
            layer = ''.join(layer)

            layer = dsp.pad(layer, grain_length / index, 0)
            layers += [ layer ]

        out = dsp.mix(layers, True, 10)

    if envelope == True:
        out = dsp.env(out, envelope)

    if buffer_index:
        fname = 'samps/buf-%s' % str(buffer_index)
        if os.path.exists(fname + '.wav') and overdub == False:
            pass
        else:
            dsp.write(out, fname)

    if pan:
        out = dsp.pan(out, dsp.rand())

    return out
