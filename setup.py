from setuptools import setup

setup(name='pippic',
        version='1.0.0b1',
        description='A command interface for the pippi computer music system',
        url='http://hecanjog.github.com/pippi-console',
        author='He Can Jog',
        author_email='erik@hecanjog.com',
        license='Public Domain',

        classifiers = [
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 2.7',  
        ],

        keywords = 'music dsp improvisation livecoding',

        packages=['pippic'],

        package_data={'pippic': [
            'data/types.json', 
            'data/orc_example.py', 
            'data/readme.md',
            'data/gitignore.default',
        ]},

        install_requires=['pippi', 'termcolor', 'docopt', 'dumptruck'],
        scripts=['bin/pippi'],
        zip_safe=False
    )
