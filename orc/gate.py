from pippi import dsp

shortname   = 'ga'
name        = 'gate'
device      = 'default'
loop        = True

def play(params):
    length = params.get('length', dsp.stf(2))
    reps   = params.get('repeats', 4)

    out = ''
    stream = []
    for rep in range(reps):
        stream += [ ('/tick/6', 1, dsp.fts(length / 2)) ]
        stream += [ ('/tick/6', 0, dsp.fts(length / 2)) ]
        out += dsp.pad(dsp.amp(dsp.tone(length / 2), 0.1), 0, length/ 2)
    
    return (out, {'value': {'events': [ stream ]}})
