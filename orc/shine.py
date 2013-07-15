from pippi import dsp
from pippi import tune

shortname   = 'sh'
name        = 'shine'
#device      = 'T6_pair1'
device      = 'default'
loop        = True

# Generator-specific param types (unimplemented)
types       = {
    'o': {
        'name': 'octave',
        'type': 'integer',
        'accepts': ['integer'],
    }
}

def play(params):
    """ Usage:
            shine.py [length] [volume]
    """
    length      = params.get('length', dsp.stf(dsp.rand(0.1, 1)))
    volume      = params.get('volume', 20.0)
    volume = volume / 100.0 # TODO: move into param filter
    octave      = params.get('octave', 2) + 1 # Add one to compensate for an old error for now
    note        = params.get('note', ['c'])
    note = note[0]
    quality     = params.get('quality', tune.major)
    glitch      = params.get('glitch', False)
    superglitch = params.get('superglitch', False)
    pinecone    = params.get('pinecone', False)
    glitchpad   = params.get('glitch-padding', 0)
    glitchenv   = params.get('glitch-envelope', False)
    env         = params.get('envelope', False)
    ratios      = params.get('ratios', tune.terry)
    pad         = params.get('padding', False)
    bend        = params.get('bend', False)
    bpm         = params.get('bpm', 75.0)
    width       = params.get('width', False)
    wform       = params.get('waveform', False)
    instrument  = params.get('instrument', 'r')
    scale       = params.get('scale', [1,6,5,4,8])
    shuffle     = params.get('shuffle', False) # Reorganize input scale
    reps        = params.get('repeats', len(scale))
    alias       = params.get('alias', False)
    phase       = params.get('phase', False)
    pi          = params.get('pi', False)
    wild        = params.get('wii', False)
    root        = params.get('root', 27.5)
    trigger_id = params.get('trigger_id', 0)

    tune.a0 = float(root)

    try:
        # Available input samples
        if instrument == 'r':
            instrument = 'rhodes'
            tone = dsp.read('sounds/synthrhodes.wav').data
        elif instrument == 's':
            instrument = 'synthrhodes'
            tone = dsp.read('sounds/220rhodes.wav').data
        elif instrument == 'c':
            instrument = 'clarinet'
            tone = dsp.read('sounds/clarinet.wav').data
        elif instrument == 'v':
            instrument = 'vibes'
            tone = dsp.read('sounds/glock220.wav').data
        elif instrument == 't':
            instrument = 'tape triangle'
            tone = dsp.read('sounds/tape220.wav').data
        elif instrument == 'g':
            instrument = 'glade'
            tone = dsp.read('sounds/glade.wav').data 
        elif instrument == 'p':
            instrument = 'paperclips'
            tone = dsp.read('sounds/paperclips.wav').data
        elif instrument == 'i':
            instrument = 'input'
            tone = dsp.capture(dsp.stf(1))
    except:
        instrument = None
        tone = None

    out = ''

    # Shuffle the order of pitches
    if shuffle is not False:
        scale = dsp.randshuffle(scale)

    # Translate the list of scale degrees into a list of frequencies
    freqs = tune.fromdegrees(scale, octave, note, quality, ratios)
    freqs = [ freq / 4.0 for freq in freqs ] 

    # Format is: [ [ path, offset, id, value ] ]
    # Offset for video 
    osc_messages = [ ['/dac', float(dsp.fts(length)), 1, tune.fts(osc_freq)] for osc_freq in freqs ]

    # Phase randomly chooses note lengths from a 
    # set of ratios derived from the current bpm
    if phase is not False:
        ldivs = [0.5, 0.75, 2, 3, 4]
        ldiv = dsp.randchoose(ldivs)
        length = dsp.bpm2ms(bpm) / ldiv
        length = dsp.mstf(length)
        reps = ldiv if ldiv > 1 else 4


    # Construct a sequence of notes
    for i in range(reps):
        # Get the freqency
        freq = freqs[i % len(freqs)]

        # Transpose the input sample or 
        # synthesize tone
        if wform is False and tone is not None:
            # Determine the pitch shift required
            # to arrive at target frequency based on 
            # the pitch of the original samples.
            if instrument == 'clarinet':
                diff = freq / 293.7
            elif instrument == 'vibes':
                diff = freq / 740.0 
            else:
                diff = freq / 440.0

            clang = dsp.transpose(tone, diff)

        elif wform == 'super':
            clang = dsp.tone(length, freq, 'phasor', 0.5)
            clang = [ dsp.drift(clang, dsp.rand(0, 0.02)) for s in range(7) ]
            clang = dsp.mix(clang)

        elif wform is False and tone is None:
            clang = dsp.tone(length, freq, 'sine2pi', 0.75)
            clang = dsp.amp(clang, 0.6)

        else:
            clang = dsp.tone(length, freq, wform, 0.75)
            clang = dsp.amp(clang, 0.6)

        # Stupidly copy the note enough or 
        # trim it to meet the target length
        clang = dsp.fill(clang, length)

        # Give synth tones simple env (can override)
        if wform is not False and env is False:
            clang = dsp.env(clang, 'phasor')

        # Apply an optional amplitude envelope
        if env is not False:
            clang = dsp.env(clang, env)

        # Add optional padding between notes
        if pad != False:
            clang = dsp.pad(clang, 0, pad)

        # Add to the final note sequence
        out += clang

    # Add optional aliasing (crude bitcrushing)
    if alias is not False:
        out = dsp.alias(out)

    # Cut sound into chunks of variable length (between 5 & 300 ms)
    # Pan each chunk to a random position
    # Apply a sine amplitude envelope to each chunk
    # Finally, add variable silence between each chunk and shuffle the
    # order of the chunks before joining.
    if glitch is not False:
        out = dsp.vsplit(out, dsp.mstf(5), dsp.mstf(300))
        out = [dsp.pan(o, dsp.rand()) for o in out]

        out = [dsp.env(o, 'sine') for o in out]
    
        out = [dsp.pad(o, 0, dsp.mstf(dsp.rand(0, glitchpad))) for o in out]

        out = ''.join(dsp.randshuffle(out))

    # Detune between 1.01 and 0.99 times original speed 
    # as a sine curve whose length equals the total output length
    if bend is not False:
        out = dsp.split(out, 441)
        freqs = dsp.wavetable('sine', len(out), 1.01, 0.99)
        out = [ dsp.transpose(out[i], freqs[i]) for i in range(len(out)) ]
        out = ''.join(out)

    if wild is not False:
        #out = dsp.vsplit(out, 400, 10000)
        out = dsp.split(out, 3000)
        out = [ dsp.amp(dsp.amp(o, dsp.rand(10, 50)), 0.5) for o in out ]
        #out = [ o * dsp.randint(1, 5) for o in out ]
        for index, o in enumerate(out):
            if dsp.randint(0, 1) == 0:
                out[index] = dsp.env(dsp.cut(o, 0, dsp.flen(o) / 4), 'gauss') * 4 

            if dsp.randint(0, 6) == 0:
                out[index] = dsp.transpose(o, 8) 

        out = [ dsp.env(o, 'gauss') for o in out ]
        freqs = dsp.wavetable('sine', len(out), 1.02, 0.98)
        out = [ dsp.transpose(out[i], freqs[i]) for i in range(len(out)) ]
        out = ''.join(out)

    if pinecone == True:
        out = dsp.pine(out, int(length * dsp.rand(0.5, 8.0)), dsp.randchoose(freqs) * dsp.rand(0.5, 4.0))

    # Adjust output amplitude as needed and return audio + OSC 
    if pi:
        return (dsp.amp(out, volume), {'osc': osc_messages})
    else:
        return dsp.amp(out, volume)

#dsp.pipe(play)
