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

setup(
    name='xnova',
    packages=['xnova'],  # this must be the same as the name above
    version='0.0.1',
    description='Xnova is an open source implementation of the browser game'
                'OGame',
    long_description=open('README.md').read(),
    license='GPLv3',
    author='Rafel Arquero',
    author_email='rafael@arque.ro',
    url='https://github.com/xnova/xnova',  # use the URL to the github repo
    download_url='https://github.com/xnova/xnova/tarball/0.0.1',
    keywords=['xnova', 'django', 'ogame'],  # arbitrary keywords
    classifiers=[],
    cmdclass=cmdclass,
    )
