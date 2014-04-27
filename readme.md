Pippi console currently depends on ALSA, and is therefore linux-only. [The core dsp system is however fully cross platform.](https://github.com/hecanjog/pippi)

## Quick start

Pippi only supports python 2.7.x at the moment, so verify that's what you're using

    $ python --version

### Install pippi-console for all users from source

    $ sudo python setup.py install

### Create a new pippi project

    $ pippi new acoolproject

### Start pippi

    $ cd acoolproject
    $ pippi

### Run the example generator script

    ^_- ex re

The `^_- ` is just the cheeky prompt for the pippi console. 

The first command `ex` is the generator script's 'shortname'. (Short for example of course!)

The second command `re` tells pippi to regenerate the buffer produced by the script after each play, so as the 
output of the script loops, you may modify it to change the behavior.

While the generator plays, open the file 'example.py' in the 'orc' directory with your favorite text editor and 
find the line that reads `freq = tune.ntf('a', octave=2)`. 

Try changing `'a'` to `'e'` or `'f#'`. Or maybe try changing `octave=2` to `octave=4` or `octave=10`. Or find 
`sine2pi` and try changing it to `tri`, `impulse`, `vary` or `hann`.

Check out the documentation for pippi for more code examples you can use in generator scripts. 
I also have a small but growing collection of instruments and recipes for pippi in my [hcj.py](https://github.com/hecanjog/hcj.py) repo.

