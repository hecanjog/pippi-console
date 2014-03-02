import os
import time
from pippi import dsp
from pippic import param
from pippic import osc 
from pippic import settings
import multiprocessing as mp
import alsaaudio

def grid(tick, bpm):
    os.nice(0)

    bpm = dsp.mstf(dsp.bpm2ms(bpm))

    count = 0
    while True:
        tick.set()
        tick.clear()
        dsp.delay(bpm)
        count += 1

def render(play, voice_id, once, uno):
    os.nice(19)
    current = mp.current_process()

    out = play(voice_id)

    if once == True:
        settings.voice(voice_id, 'once', False)

    settings.buffer(voice_id, out)

def dsp_loop(out, buffer, voice_id):
    os.nice(0)

    target_volume = settings.voice(voice_id, 'volume')
    post_volume   = settings.voice(voice_id, 'post_volume')

    buffer = dsp.split(buffer, 500)

    for chunk in buffer:
        if target_volume != post_volume:
            if target_volume > post_volume:
                post_volume += 0.01
            elif post_volume > target_volume:
                post_volume -= 0.01

            chunk = dsp.amp(chunk, post_volume)

        out.write(chunk)

        if post_volume < 0.002:
            settings.voice(voice_id, 'loop', False)
            settings.voice(voice_id, 'post_volume', post_volume)
            break

    settings.voice(voice_id, 'post_volume', post_volume)

def out(generator, tick):
    """ Master playback process spawned by play()
        Manages render and playback processes  

        Params are collapsed to a key-value dict,
        where the value is translated to the target 
        data type, and the key is expanded to the param
        full name.
        """

    # Give this process a high priority to help prevent unwanted audio glitching
    #os.nice(-19)

    voice_id = str(mp.current_process().name)

    # Spawn a render process which will write generator output
    # into the buffer for this voice
    r = mp.Process(name='r' + str(voice_id), target=render, args=(generator.play, voice_id, False, False))
    r.start()
    r.join()

    # Open a connection to an ALSA PCM device
    device = settings.param(voice_id, 'device')

    try:
        out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, device)
    except:
        print 'Could not open an ALSA connection.'
        return False

    out.setchannels(2)
    out.setrate(44100)
    out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    out.setperiodsize(10)

    # On start of playback, check to see if we should be regenerating 
    # the sound. If so, spawn a new render thread.
    # If there is a fresher render available, use that instead.
    cooking             = False # Flag set to true if a render subprocess has been spawned
    volume              = 1.0
    next                = False

    buffer = settings.buffer(voice_id)
    while settings.voice(voice_id, 'loop') == True:
        regenerate    = settings.voice(voice_id, 'regenerate')
        once          = settings.voice(voice_id, 'once')
        uno           = settings.voice(voice_id, 'uno')
        quantize      = settings.voice(voice_id, 'quantize')
        target_volume = settings.voice(voice_id, 'volume')

        if uno == True:
            settings.param(voice_id, 'loop', False)

        if regenerate == True or once == True:
            reload(generator)
            r = mp.Process(name='r' + str(voice_id), target=render, args=(generator.play, voice_id, False, False))
            try:
                r.start()
                r.join()
                buffer = settings.buffer(voice_id)
            except OSError:
                pass # Lame. Rehearsal is in an hour tho.

        if quantize != False:
            tick.wait()

        dsp_loop(out, buffer, voice_id)

    settings.remove_voice(voice_id)

def capture(length=44100, device='default', numchans=2):
    input = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, device)
    input.setchannels(numchans)
    input.setrate(44100)
    input.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    input.setperiodsize(100)

    out = ''
    count = 0
    while count < length:
        rec_frames, rec_data = input.read()
        count += rec_frames
        out += rec_data

    return out

