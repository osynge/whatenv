from osweint.__version__ import version
from sys import version_info

try:
    from setuptools import setup, find_packages
except ImportError:
	try:
            from distutils.core import setup
	except ImportError:
            from ez_setup import use_setuptools
            use_setuptools()
            from setuptools import setup, find_packages
import os

Application = 'whatenv'

def determine_path ():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        return os.path.dirname (os.path.abspath (root))
    except:
        print "I'm sorry, but something is wrong."
        print "There is no __file__ variable. Please contact the author."
        sys.exit ()
# we want this module for nosetests
try:
    import multiprocessing
except ImportError:
    # its not critical if this fails though.
    pass


setup(name=Application,
    version=version,
    description="""Simple set of scritps to build up and tear down clusters in an Open Stack enviroment.""",
    author="O M Synge",
    author_email="owen.synge@suse.de",
    license='Apache Sytle License (2.0)',
    install_requires=[
       "nose >= 1.1.0",
       "setuptools",
        ],    
    tests_require=[
        'coverage >= 3.0',
        'nose >= 1.1.0',
        'mock',
    ],
    setup_requires=[
        'nose',
    ],

    test_suite = 'nose.collector',
    url = 'https://github.com/osynge/whatenv.git',
    packages = ['osweint'],
    classifiers=[
        'Development Status :: 1 - UnStable',
        'Environment :: GUI',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    scripts=['whatenv_teardown', 'whatenv_buildup', 'whatenv_debounce'],
    data_files=[('%s-%s' % (Application,version),['README.md',
            'LICENSE',
            'ChangeLog',
            'steering_example.json',
            'whatenv_example.cfg']),
        ]    
)
