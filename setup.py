from setuptools import setup

setup(name='pippi',
        version='0.3.0',
        description='A command interface for the pippi computer music system',
        url='http://hecanjog.github.com/pippi-console',
        author='He Can Jog',
        author_email='erik@hecanjog.com',
        license='Public Domain',
        packages=['pippic'],
        install_requires=['distribute', 'pippi', 'pyalsaaudio', 'termcolor', 'pyliblo', 'docopt'],
        test_suite='nose.collector',
        tests_require=['nose'],
        scripts=['bin/pippi'],
        zip_safe=False)
