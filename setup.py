import os
from distutils.core import setup, Command

os.environ['DJANGO_SETTINGS_MODULE'] = 'xnova.tests.settings'

cmdclass = {}


class TestCommand(Command):
    description = "run package tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from xnova.tests.utils import run_tests

        run_tests()


cmdclass['test'] = TestCommand

import xnova

setup(
    name='xnova',
    version=xnova.__version__,
    license=xnova.__license__,
    description='Xnova is an open source implementation of the browser game'
                'OGame',
    long_description=open('README.md').read(),
    author=xnova.__author__,
    author_email=xnova.__email__,
    packages=['xnova'],  # this must be the same as the name above
    keywords=['xnova', 'django', 'ogame'],
    classifiers=[],  # TODO(arkeros)
    url='https://github.com/xnova/xnova',  # use the URL to the github repo
    download_url='https://github.com/xnova/xnova/tarball/0.0.1',
    cmdclass=cmdclass,
    )
