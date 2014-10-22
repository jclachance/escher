from sys import argv
from subprocess import call
import threading
import webbrowser
import os
from shutil import copy
from os.path import join, dirname, realpath, exists
from glob import glob
    
try:
    from setuptools import setup, Command
except:
    from distutils.core import setup, Command

directory = dirname(realpath(__file__))
version = __import__('escher').__version__
escher = 'escher.%s.js'%version
escher_min = 'escher.%s.min.js'%version
port = 8789

class CleanCommand(Command):
    description = "Custom clean command that removes escher lib files"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        def remove_if(x):
            if exists(x): os.remove(x)
        remove_if(join(directory, 'build'))
        remove_if(join(directory, 'dist'))
        # remove lib files
        for f in glob(join(directory, 'escher/lib/escher.*.js')):
            os.remove(f)
        # remove site files
        for f in glob(join(directory, '*.html')):
            os.remove(f)
        print 'done cleaning'

class JSBuildCommand(Command):
    description = "Custom build command that generates escher lib files"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        call(['node',
              join(directory, 'bin', 'r.js'),
              '-o', join('escher', 'js', 'build', 'build.js'),
              'out='+join('escher', 'lib', escher),
              'optimize=none'])
        call(['node',
              join(directory, 'bin', 'r.js'),
              '-o', join('escher', 'js', 'build', 'build.js'),
              'out='+join('escher', 'lib', escher_min),
              'optimize=uglify'])
        print 'done building js'
        
class BuildGHPagesCommand(Command):
    description = "Custom build command that generates static site, and copies escher libs"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # copy files to top level
        copy(join('escher', 'lib', escher), '.')
        copy(join('escher', 'lib', escher_min), '.')
        copy(join('escher', 'lib', escher), 'escher.js')
        copy(join('escher', 'lib', escher_min), 'escher.min.js')
        # generate the static site
        call(['python', join('escher', 'static_site.py')])
        call(['python', join('escher', 'generate_index.py')])
        print 'Done building gh-pages'

class TestCommand(Command):
    description = "Custom test command that runs pytest and jasmine"
    user_options = [('jsonly', None, 'Only run jasmine tests'),
                    ('pyonly', None, 'Only run pytest')]
    def initialize_options(self):
        self.jsonly = False
        self.pyonly = False
    def finalize_options(self):
        pass
    def run(self):
        if not self.jsonly:
            call('py.test', shell=True)
        if not self.pyonly:
            call(['jasmine', '--port=%d' % port])
        
setup(name='Escher',
      version=version,
      author='Zachary King',
      url='http://zakandrewking.github.io/escher/',
      packages=['escher'],
      package_data={'escher': ['css/*', 'templates/*', 'example_data/*',
                               'lib/*.js', 'lib/*.css', 'lib/fonts/*',
                               'resources/*']},
      cmdclass={'clean': CleanCommand,
                'buildjs': JSBuildCommand,
                'buildgh': BuildGHPagesCommand,
                'test': TestCommand})
