
import argparse
import chevron
from copy import deepcopy
import logging
from os import getcwd
from os.path import isfile, join, splitdrive
import re
import yaml
from mustacheyou.base import MustacheYouBase

logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG, filename="stacher.log", encoding='utf-8')

# if __name__ == "__main__":
def make():
    parser = argparse.ArgumentParser(description='Process MustacheYou config.')
    parser.add_argument('--infile', '-i', required=True,
                        help='Input YAML file')
    parser.add_argument('--outdir', '-o',
                        help='Output folder for MustacheYou results')
    parser.add_argument('--mustache', '--templates', '-t', '-m',
                        help='Template file in Mustache syntax or a folder of such files')
    parser.add_argument('--yaml_path', nargs='*', type=str,
                        help='To use only a subset of the YAML input file based on a path of mappings')
    args = parser.parse_args()
    infile = args.infile
    drive = splitdrive(infile)
    # logging.info(f"Infile: {args.infile}")
    if not re.match('^[/]', infile) and drive[0] == '':
        infile = join(getcwd(), infile)
        # logging.info(f"Updated infile with CWD: {infile}")
    if not isfile(infile):
        raise Exception(f"No such file as infile {infile}")
    maker = MustacheYou(infile, args.outdir, args.mustache, args.yaml_path)
    maker.make()

class MustacheYou(MustacheYouBase):
    extra_template_dirs = []
    def __init__(self, yaml_config, dest_dir=None, extra_template_dirs=None, yaml_path=None):
        if extra_template_dirs:
            self.extra_template_dirs.extend([x.strip() for x in extra_template_dirs.split(',')])
        # self.dest_dir = dest_dir
        config = None
        if isinstance(yaml_config, list):
            config = {}
            for better_be_a_dict in yaml_config:
                data = deepcopy(config.get('data', {}))
                for key, value in better_be_a_dict.items():
                    config[key] = value
                for key, value in better_be_a_dict.get('data', {}).items():
                    data[key] = value
                config['data'] = data
            # TODO MAYBE SOMEDAY: Let list be a list of strings - and combine more than one YAML file the same way we combine dicts.
        elif isinstance(yaml_config, dict):
            config = yaml_config
        else:
            self.yaml_file = yaml_config
            with open(self.yaml_file, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    logging.error(f"Failed to parse YAML file {self.yaml_file}: {exc}")
                    raise exc

        if not extra_template_dirs:
            self.extra_template_dirs = config.get('mustache', ['.'])
        # logging.info(f"extra_template_dirs {self.extra_template_dirs}")
        if not isinstance(self.extra_template_dirs, list):
            self.extra_template_dirs = [self.extra_template_dirs]
        # logging.info(f"extra_template_dirs {self.extra_template_dirs}")
        outdir = dest_dir
        if not outdir:
            outdir = config.get('outdir', 'mustached')
        config['outdir'] = outdir
        config['mustache_templates_dir'] = self.extra_template_dirs[0]
        # logging.info(f"mustache_templates_dir {config['mustache_templates_dir']}")
        if extra_template_dirs and len(extra_template_dirs) > 1:
           config['extra_template_dirs'] = self.extra_template_dirs[1:]
        if yaml_path:
            config['yaml_path'] = yaml_path
        logging.info(f"Top config: outdir {outdir}, mustache_templates_dir {config['mustache_templates_dir']}, extra_template_dirs {extra_template_dirs}, yaml_path {yaml_path}")
        logging.info(f"Config: {config}")

        super().__init__(config)
    def make(self):
        result = True
        if not super().make():
            result = False
        return result
