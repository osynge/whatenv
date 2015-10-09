from osweint.__version__ import version
from sys import version_info
import os
try:
    from setuptools import setup, find_packages, Command
except ImportError:
	try:
            from distutils.core import setup, Command
	except ImportError:
            from ez_setup import use_setuptools, Command
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


class CustomTags(Command):
    user_options = []
    def __init__(self, *args, **kwargs):


        self.packaging = "default value for this option"

        # 'finalized' records whether or not 'finalize_options()' has been
        # called.  'finalize_options()' itself should not pay attention to
        # this flag: it is the business of 'ensure_finalized()', which
        # always calls 'finalize_options()', to respect/update it.
        self.finalized = 0
    def run(self):
        import subprocess
        cmd = "ctags -L -"
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True )
        FILE_TYPE_LIST = ["py"]
        codeRootDir = os.getcwd()
        for root,dirs,files in os.walk(codeRootDir):
            for file in files:
                for file_type in FILE_TYPE_LIST:
                    if file.split('.')[-1] == file_type:
                        process.stdin.write('%s\n' %os.path.join(root,file))
    def finalize_options(self):
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
        ],
    cmdclass={
            'tags': CustomTags
        }
)
