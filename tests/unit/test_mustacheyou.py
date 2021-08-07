
from os import popen
from os.path import dirname, join
import re
from mustacheyou.maker import MustacheYou
from tempfile import NamedTemporaryFile

def test_make():
    this_dir = dirname(__file__)
    maker = MustacheYou(join(this_dir, 'test_mustacheyou.yml'),
                           join(this_dir, 'temp.d'))
    assert maker.make()

def test_django_startproject():
    tmpf = NamedTemporaryFile()
    # stream = os.popen('pwd')
    # output = stream.read()
    # assert re.search('xxx', output)
    stream = popen('pip list')
    output = stream.read()
    assert re.search('mustacheyou', output)
