
import argparse
import chevron
import logging
from os import getcwd
from os.path import isfile, join, splitdrive
import re
import yaml
from mustacheyou.base import MustacheYouBase

logging.basicConfig(level=logging.DEBUG)

# if __name__ == "__main__":
def make():
    parser = argparse.ArgumentParser(description='Process MustacheYou config.')
    parser.add_argument('--infile', '-i', required=True,
                        help='Input YAML file')
    parser.add_argument('--outdir', '-o',
                        help='Output folder for MustacheYou results')
    parser.add_argument('--mustache', '--templates', '-t', '-m',
                        help='Template folder with files in Mustache syntax')
    parser.add_argument('--yaml_path', nargs='*', type=str, help='To use only a subset of the YAML input file based on a path of mappings')
    args = parser.parse_args()
    infile = args.infile
    drive = splitdrive(infile)
    # logging.info(f"Infile: {args.infile}")
    if not re.match('^[/]', infile) and drive[0] == '':
        infile = join(getcwd(), infile)
        # logging.info(f"Updated infile with CWD: {infile}")
    if not isfile(infile):
        logging.error(f"No such file as infile {infile}")
    maker = MustacheYou(args.infile, args.outdir, args.mustache)
    maker.make()

class MustacheYou(MustacheYouBase):
    extra_template_dirs = []
    def __init__(self, yaml_file, dest_dir=None, extra_template_dirs=None):
        self.yaml_file = yaml_file
        # self.dest_dir = dest_dir
        if extra_template_dirs:
            self.extra_template_dirs.extend([x.strip() for x in extra_template_dirs.split(',')])
        with open(yaml_file, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logging.error(f"Failed to parse YAML file {yaml_file}: {exc}")
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

        super().__init__(config)
    def make(self):
        result = True
        if not super().make():
            result = False
        return result
