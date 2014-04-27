from pippi import dsp
from pippi import tune

# Un-pythonic shortcuts, but makes live coding easier
from pippic.settings import get_param as P
from pippic.settings import config as C

shortname   = 'ex'
name        = 'example'

def play(voice_id):
    """ Every generator script must define a play() function, which 
        accepts a voice_id integer (so you can read and write params 
        for each voice) and returns a sound.
        
        The shortname and name metadata above are optional, if you 
        don't include them the name will be drawn from the filename 
        and the shortname will be the first two characters of that name.
    """

    # Get the current bpm set in our session
    bpm = C('bpm')

    # Convert it to a length in frames
    beat = dsp.bpm2frames(bpm)

    # Read per-instance param, with a default value
    volume = P(voice_id, 'volume', default=1.0)

    # Get a frequency for the beep
    freq = tune.ntf('a', octave=2)

    # Beep for a beat
    out = dsp.tone(length=beat, freq=freq, wavetype='sine2pi', amp=volume)

    # Be silent for a beat after the beep
    out = dsp.pad(out, 0, beat)

    # Log the length of the computed buffer. 
    # I like to tail -f pippi.log during performance.
    dsp.log('voice %s length: %.2f' % (voice_id, dsp.fts(dsp.flen(out))))

    # Pass along the final buffer for playback
    return out
