from pippi import dsp

shortname = 'ce'
name      = 'cell'
device    = 'default'
loop      = True

def play(params={}):
    length = params.get('length', dsp.stf(3))

    def bln(length, low=3000.0, high=7100.0, wform='sine2pi'):
        wforms = ['tri', 'sine2pi', 'impulse', 'cos2pi']
        outlen = 0
        cycles = ''
        while outlen < length:
            cycle = dsp.cycle(dsp.rand(low, high), dsp.randchoose(wforms))
            outlen += len(cycle)
            cycles += cycle

        return cycles

    envs = ['phasor', 'line', 'sine']

    hats = [ bln(dsp.mstf(dsp.rand(100, 1000)), dsp.rand(200, 5000), dsp.rand(3000, 11000)) for i in range(32) ]
    hats = [ dsp.env(hat, dsp.randchoose(envs)) for hat in hats ]
    hats = [ dsp.pad(hat, 0, dsp.mstf(170)) for hat in hats ]
    hats = ''.join(hats)

    return hats
