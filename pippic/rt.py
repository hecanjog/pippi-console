import os
import time
from pippi import param
from pippi import dsp
from pippi import osc 
import multiprocessing as mp
import alsaaudio

def grid(tick, bpm):
    os.nice(-19)

    bpm = dsp.mstf(dsp.bpm2ms(bpm))

    count = 0
    while True:
        tick.set()
        tick.clear()
        dsp.delay(bpm)
        count += 1

def render(play, buffers, voice_params, once, uno):
    current = mp.current_process()
    buffer_type = current.name[0]
    voice_id = current.name[1:]

    params = getattr(voice_params, voice_id).collapse()

    out = play(params)

    sound, data = (out[0], out[1]) if len(out) == 2 else (out, None) 

    if data is not None:
        params = getattr(voice_params, voice_id)
        params.data['data'] = data
        setattr(voice_params, voice_id, params)

    if once == True:
        params = getattr(voice_params, voice_id)
        params.set('once', False)
        setattr(voice_params, voice_id, params)

    buffer_id = 'n' + voice_id if buffer_type == 'n' else voice_id

    setattr(buffers, buffer_id, dsp.split(sound, 500))

def dsp_loop(out, buffer, params, voice_params, voice_id, jack=False):
    params = getattr(voice_params, voice_id)

    target_volume = params.get('target_volume', 1.0)
    post_volume   = params.get('post_volume', 1.0)

    for chunk in buffer:
        if target_volume != post_volume:
            if target_volume > post_volume:
                post_volume += 0.01
            elif post_volume > target_volume:
                post_volume -= 0.01

            chunk = dsp.amp(chunk, post_volume)

        out.write(chunk)

        if post_volume < 0.002:
            params = getattr(voice_params, voice_id)
            params.set('loop', False)
            params.set('post_volume', post_volume)
            setattr(voice_params, voice_id, params)
            break

    params = getattr(voice_params, voice_id)
    params.set('post_volume', post_volume)
    setattr(voice_params, voice_id, params)

def out(generator, buffers, voice_params, tick):
    """ Master playback process spawned by play()
        Manages render and playback processes  

        Params are collapsed to a key-value dict,
        where the value is translated to the target 
        data type, and the key is expanded to the param
        full name.
        """

    # Give this process a high priority to help prevent unwanted audio glitching
    os.nice(-19)

    voice_id = mp.current_process().name

    # Fetch voice params from namespace
    params = getattr(voice_params, voice_id).collapse()

    # Spawn a render process which will write generator output
    # into the buffer for this voice
    r = mp.Process(name='r' + voice_id, target=render, args=(generator.play, buffers, voice_params, False, False))
    r.start()
    r.join()

    # Fetch the buffer that was just filled
    buffer = getattr(buffers, voice_id)

    # Open a connection to an ALSA PCM device
    device = params.get('device', 'default')

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

    while params.get('loop', True) == True:
        params = getattr(voice_params, voice_id).collapse()
        active = mp.active_children()

        regenerate    = params.get('regenerate', False)
        once          = params.get('once', False)
        uno           = params.get('uno', False)
        quantize      = params.get('quantize', False)
        target_volume = params.get('target_volume', 1.0)


        if uno == True:
            params = getattr(voice_params, voice_id)
            params.set('loop', False)
            setattr(voice_params, voice_id, params)
            params = getattr(voice_params, voice_id).collapse()

        if hasattr(buffers, 'n' + voice_id):
            buffer = getattr(buffers, 'n' + voice_id)
            setattr(buffers, voice_id, buffer)
            delattr(buffers, 'n' + voice_id)

        if len(active) == 0 and (regenerate is True or once is True):
            reload(generator)
            next = mp.Process(name='n' + voice_id, target=render, args=(generator.play, buffers, voice_params, once, uno))
            next.start()

        active = mp.active_children()
        if len(active) == 0:
            buffer = getattr(buffers, voice_id)

        if quantize is not False:
            tick.wait()

        dsp_loop(out, buffer, params, voice_params, voice_id)
        params = getattr(voice_params, voice_id).collapse()

    # Cleanup 
    delattr(voice_params, voice_id)
    delattr(buffers, voice_id)

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

