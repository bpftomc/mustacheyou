
from os import chdir, popen, remove
from os.path import basename, dirname, isfile, join
import re
from shutil import rmtree
import yaml
from mustacheyou.stacher import MustacheYou
# from tempfile import NamedTemporaryFile

# this_dir = dirname(__file__)
this_file = basename(__file__)
chdir('tests/unit')

def test_make():
    # config_file = join(this_dir, 'test_mustacheyou.yml')
    config_file = 'test_mustacheyou.yml'
    if not isfile(config_file):
        # config_file = join(this_dir, 'test_mustacheyou.yaml')
        config_file = 'test_mustacheyou.yaml'
    assert isfile(config_file)
    # maker = MustacheYou(config_file, join(this_dir, 'temp.d'))
    maker = MustacheYou(config_file, 'temp.d', '.')
    assert maker.make()
    assert isfile(join('temp.d', this_file))
    rmtree('temp.d')

def test_pip():
    # tmpf = NamedTemporaryFile()
    # stream = os.popen('pwd')
    # output = stream.read()
    # assert re.search('xxx', output)
    stream = popen('pip list')
    output = stream.read()
    assert re.search('mustacheyou', output)

def test_command_line():
    # stream = popen(f'cd {this_dir} && ../../bin/mustacheyou --infile ./test_mustacheyou.yml --outdir test.d')
    stream = popen('../../bin/mustacheyou --infile ./test_mustacheyou.yml --outdir mustache_done')
    output = stream.read()
    assert not output
    # assert isfile(join(this_dir, 'mustached', 'templateFile.txt'))
    assert isfile(join('mustache_done', 'templateFile.txt'))
    assert isfile(join('mustache_done/source_subdir', '.gitkeep'))
    assert not isfile(join('mustache_done', 'excludeMe.txt'))
    assert isfile(join('must_out/subdir_dest', '.gitkeep'))

    with open(join('mustache_done', 'templateFile.txt'), 'r') as testf:
        content = testf.read()
        assert re.search('asy as 123', content)
        assert re.search('Next: The next three after 123', content)
        assert re.search('Key interpolation: -dingo-', content)

    stream = popen('diff -r properly_mustached mustache_done')
    output = stream.read()
    assert not output

    rmtree('mustache_done')
    rmtree('must_out')

def test_single_file():
    stream = popen('../../bin/mustacheyou -i ./test_mustacheyou2.yaml -m templates2/this_file.json')
    output = stream.read()
    assert not output
    assert isfile(join('yml_file_outdir', 'this_file.json'))
    # with open(join('mustache_done', 'templateFile.txt'), 'r') as testf:
    #     content = testf.read()
    #     assert re.search('asy as 123', content)
    #     assert re.search('Next: The next three after 123', content)
    #     assert re.search('Key interpolation: -dingo-', content)
    rmtree('yml_file_outdir')

def test_yaml_path():
    cmd = '../../bin/mustacheyou -i ./test_mustacheyou2.yaml -m templates2/this_file.json'
    stream = popen(f"{cmd} --yaml_path files this_file")
    output = stream.read()
    assert not output
    assert isfile(join('yml_file_outdir', 'this_file.json'))
    with open(join('yml_file_outdir', 'this_file.json'), 'r') as testf:
        content = testf.read()
        assert re.search('some": "thing', content)
        assert re.search('loves": "your .*face', content)
    rmtree('yml_file_outdir')

def test_list_of_config():
    target_file = 'this_file.json'
    config_file = 'test_mustacheyou2.yaml'
    assert isfile(config_file)
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)
    configs = [config]
    for f in config['data']['file_list']:
        if f['name'] == target_file:
            configs.append({'data': f})
    maker = MustacheYou(configs, 'temp.d2', 'templates2')
    assert maker.make()
    assert isfile(join('temp.d2', target_file))
    with open(join('temp.d2', 'this_file.json'), 'r') as testf:
        content = testf.read()
        assert re.search('some": "body once told me', content)
        assert re.search('loves": "yer momma', content)
    rmtree('temp.d2')
