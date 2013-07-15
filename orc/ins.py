from pippi import dsp
from pippi import rt
from pippi import tune

shortname       = 'in'
name            = 'ins'
device          = 'T6_pair1'
#device          = 'default'
loop            = True

def play(params):
    length          = params.get('length', dsp.mstf(2000))
    buffer_length   = params.get('buffer', dsp.mstf(2000))
    volume          = params.get('volume', 100.0)
    volume          = volume / 100.0
    scale           = params.get('scale', [1, 5])
    octave          = params.get('octave', 3)
    envelope        = params.get('envelope', False)
    pad             = params.get('pad', False)
    pinecone = params.get('pinecone', False)

    freqs = tune.fromdegrees(scale, octave, 'a')
    speeds = [ freq / 220.0 for freq in freqs ]

    out = ''
    input = rt.capture(buffer_length, 'T6_pair1', 1)

    grain_length = dsp.flen(input) / 4 

    input = dsp.vsplit(input, int(grain_length * 0.5), grain_length)
    numgrains = (length / grain_length) * 2

    if len(input) < numgrains:
        for i in range(numgrains - len(input)):
            input += [ dsp.randchoose(input) ]

    out = []

    for index in range(1, 20):
        layer = dsp.randshuffle(input)

        if pad is not False:
            layer = [ dsp.pad(grain, 0, dsp.mstf(dsp.randint(0, 800))) for grain in layer ]

        layer = [ dsp.env(grain, 'sine') for grain in layer ]
        layer = [ dsp.transpose(grain, dsp.randchoose(speeds)) for grain in layer ]
        layer = ''.join(layer)

        layer = dsp.pad(layer, grain_length / index, 0)
        out += [ layer ]

    out = dsp.mix(out, True, 10)

    if envelope is not False:
        out = dsp.env(out, envelope)

    if pinecone == True:
        # Do it in packets
        # Start from position P, take sample of N length (audio rates), apply envelope, move to position P + Q, repeat
        startlen = dsp.flen(out)
        #num_layers = dsp.randint(3, 7)
        num_layers = 1
        #num_points = dsp.randint(50, 500)
        num_points = 50
        pad_curves = [ dsp.breakpoint([ dsp.rand(0, 50) for p in range(dsp.randint(5, 15)) ], num_points) for i in range(num_layers) ]
        #pad_curves = [ [ dsp.rand(0, 150) for p in range(num_points) ] for i in range(num_layers) ]
        len_curves = [ dsp.breakpoint([ dsp.rand(5, 90) for p in range(dsp.randint(5, 15)) ], num_points) for i in range(num_layers) ]
        pos_curves = [ dsp.breakpoint([ dsp.rand(0, 1) for p in range(dsp.randint(5, 15)) ], num_points) for i in range(num_layers) ]
        pan_curves = [ dsp.breakpoint([ dsp.rand(0, 1) for p in range(dsp.randint(5, 15)) ], num_points) for i in range(num_layers) ]
        amp_curves = [ dsp.breakpoint([ dsp.rand(0, 1) for p in range(dsp.randint(15, 35)) ], num_points) for i in range(num_layers) ]

        pminlen = dsp.mstf(60)
        pmaxlen = dsp.mstf(500)
    
        pinecones = []

        for pinecone in range(num_layers):
            segment = dsp.cut(out, dsp.randint(0, dsp.flen(out) - pmaxlen), dsp.randint(pminlen, pmaxlen))

            pad_curve = pad_curves[pinecone]
            len_curve = len_curves[pinecone]
            pos_curve = pos_curves[pinecone]
            pan_curve = pan_curves[pinecone]
            amp_curve = amp_curves[pinecone]

            grains = [ dsp.cut(segment, pos_curve[i] * dsp.flen(segment) - dsp.mstf(len_curve[i]), dsp.mstf(len_curve[i])) for i in range(num_points) ]

            grains = [ dsp.pad(grains[i], 0, int(dsp.mstf(pad_curve[i]))) for i in range(num_points) ]
            grains = [ dsp.pan(grains[i], pan_curve[i]) for i in range(num_points) ]
            grains = [ dsp.amp(grains[i], amp_curve[i]) for i in range(num_points) ]
            #grains = [ dsp.env(grain, 'sine') for grain in grains ]

            pinecones += [ ''.join(grains) ]

        out = dsp.mix([dsp.pan(pinecone, dsp.rand()) for pinecone in pinecones])

        #if dsp.flen(out) > startlen:
            #out = dsp.cut(out, 0, startlen)



    return out
