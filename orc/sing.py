""" Requires sox and text2wave (via festival)
"""

from pippi import dsp
from pippi import tune
import subprocess
import os
import time

shortname   = 'si'
name        = 'sing'
device      = 'T6_pair2'
#device      = 'default'
loop        = True

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

def text2wave(lyrics):
    stamp = str(time.time())
    filename = 'bag-' + stamp + '.wav'
    path = os.getcwd() + '/tmp/' + filename
    cmd = "echo '%s' | /usr/bin/text2wave -o %s" % (lyrics, path)

    ret = subprocess.call(cmd, shell=True)

    words = dsp.read('tmp/' + filename).data

    return words

def singit(lyrics):
    return sings

def play(params):
    length      = params.get('length', dsp.stf(dsp.rand(0.1, 1)))
    volume      = params.get('volume', 100.0) / 100.0
    speed       = params.get('speed', dsp.rand(0.3, 0.5))
    octave      = params.get('octave', 2)
    note        = params.get('note', ['c'])[0]
    env         = params.get('envelope', False)
    pad         = params.get('padding', False)
    bend        = params.get('bend', False)
    wform       = params.get('waveform', False)
    instrument  = params.get('instrument', 'r')
    scale       = params.get('scale', [1,6,5,4,8])
    shuffle     = params.get('shuffle', False) # Reorganize input scale
    reps        = params.get('repeats', len(scale))
    alias       = params.get('alias', False)
    lyrics      = params.get('ww', '1-2-3-4-5-6-7-8-9-10').split('-')

    bpm = params.get('bpm', 100)

    if shuffle:
        lyrics = dsp.randshuffle(lyrics)

    lyrics = ' '.join(lyrics)

    words = text2wave(lyrics)
    words = sox("sox %s %s silence 1 0.1 1%% -1 0.1 1%%", words)
    words = dsp.transpose(words, speed)

    pitches = tune.fromdegrees(scale, octave=octave, root=note)

    length = dsp.flen(words) * dsp.randint(10, 14)

    sings = [ dsp.pine(words, length, pitch) for pitch in pitches ]
    sings = dsp.mix(sings)

    sings = sox("sox %s %s tempo 4.0", sings)

    out = dsp.pan(sings, dsp.rand())

    return out
