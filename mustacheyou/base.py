import copy, logging
import chevron
import os
import re

class MustacheYouBase:
    debug = False
    def __init__(self, raw_config={}, extra_config=None):
        self.raw_config = raw_config
        self.source_dir = None
        self.dest_dir = None
        self.init_useful_config(raw_config)
    def init_useful_config(self, raw_config):
        self.useful_config = raw_config.copy()
        self.useful_config['data'] = self.useful_config.get('data', {})
        if 'yaml_path' in self.raw_config:
            yaml_path_string = ">".join(self.raw_config['yaml_path'])
            follow_the_path = self.useful_config['data']
            steps = []
            for path in self.raw_config['yaml_path']:
                if path in follow_the_path:
                    steps.append(follow_the_path[path])
                    follow_the_path = follow_the_path[path]
                else:
                    raise Exception(f"Failed to find full yaml_path ({yaml_path_string}) in the given config. Lost our way at '{path}'.")
            for step in steps:
                for key, value in step.items():
                    self.useful_config['data'][key] = value
        self.recursive_render_config()
    def recursive_render_config(self, subject=None):
        if not subject:
            subject = copy.deepcopy(self.useful_config)
        result = {'rendered': subject}
        render_count = 0
        for i in range(2):
            result = self.recursive_render_dict(
                copy.deepcopy(result['rendered']),
                self.get_only_simple_values(result['rendered']))
            render_count += result['render_count']
            if result['render_count'] < 1:
                break
        logging.info(f"Render count {render_count} after {i} loops.")
        logging.info(f"Rendered {result['rendered']}.")
        self.config = result['rendered']
        return result['rendered']
    def get_only_simple_values(self, some_dict):
        return { key:value for (key,value) in some_dict.items() if not isinstance(value, list) and not isinstance(value, dict) }
    def recursive_render_dict(self, subject, data): # Returns {render_count: n, rendered: {...}}
        render_count = 0
        result = {}
        overlap_data = copy.deepcopy(data)
        overlap_data.update(subject)
        for key, value in subject.items():
            if isinstance(value, list):
                sub_result = self.recursive_render_list(value, overlap_data)
                value = sub_result['rendered']
                render_count += sub_result['render_count']
            elif isinstance(value, dict):
                sub_result = self.recursive_render_dict(value, overlap_data)
                value = sub_result['rendered']
                render_count += sub_result['render_count']
            elif isinstance(value, bool) or isinstance(value, int):
                pass # No special treatment necessary
            elif value is None:
                logging.info(f"Value for key {key} is None")
            elif '{{' in value and '{{' != value: # It cannot be the whole thing.
                # prior = value
                value = chevron.render(value, overlap_data)
                # logging.info(f"Value {value} from {prior}")
                render_count += 1
            if '{{' in key:
                # prior = key
                key = chevron.render(key, overlap_data)
                # logging.info(f"Key {key} from {prior}")
                render_count += 1
            result[key] = value
        return {'render_count': render_count, 'rendered': result}
    def recursive_render_list(self, subject, data): # Returns {render_count: n, rendered: [...]
        render_count = 0
        result = []
        for value in subject:
            if isinstance(value, list):
                sub_result = self.recursive_render_list(value, data)
                render_count += sub_result['render_count']
                value = sub_result['rendered']
            elif isinstance(value, dict):
                sub_result = self.recursive_render_dict(value, data)
                render_count += sub_result['render_count']
                value = sub_result['rendered']
            elif isinstance(value, bool) or isinstance(value, int):
                pass
            elif '{{' in value and '{{' != value: # It cannot be the whole thing.
                render_count += 1
                value = chevron.render(value, data)
            result.append(value)
        return {'render_count': render_count, 'rendered': result}

    def get_useful_config(self):
        return self.useful_config

    def make(self):
        # use_config = self.config = self.get_useful_config()
        # # use_config = self.get_useful_config()
        # if self.debug:
        #     my_type = type(self)
        #     logging.info(f"For type {my_type}, make() on useful config: {use_config}")
        self.run_all_templates()
        return True

    def run_all_templates(self, config=None):
        if config is None:
            config = self.config
        # flat_values = self.get_flat_data_values(self.config)
        for destdir, srcdir in config.get('template_dirs',{}).items():
            # logging.info(f"Config1: {config}")
            self.run_templates(srcdir, destdir, config)
        if 'outdir' in config and 'mustache_templates_dir' in config:
            # logging.info(f"Config2: {config}")
            self.run_templates(config['mustache_templates_dir'], config['outdir'], config)
        if 'outdir' in config and 'extra_template_dirs' in config:
            # logging.info(f"Config3: {config}")
            for t_dir in config['extra_template_dirs']:
                self.run_templates(t_dir, config['outdir'], config)

    def run_templates(self, srcdir0, destdir0, config=None, filename_transforms={}):
        if config is None:
            config = self.config
        # logger.info(f"run_templates(): srcdir {srcdir}, destdir {destdir}")
        if isinstance(srcdir0, dict):
            srcdir0 = srcdir0['from']
        if self.source_dir:
            srcdir = os.path.join(self.source_dir, srcdir0)
        else:
            srcdir = srcdir0
        if self.dest_dir:
            destdir = os.path.join(self.dest_dir, destdir0)
        else:
            destdir = destdir0
        if not srcdir:
            raise Exception(f"run_templates(): source dir {srcdir} is not a thing")
        if not os.path.isdir(srcdir):
            if os.path.isfile(srcdir):
                some_file = os.path.basename(srcdir)
                srcdir = os.path.dirname(srcdir)
                self.run_file(some_file, destdir, srcdir, srcdir)
            else:
                # logger.warning(f"run_templates(): source dir {srcdir} does not exist; cannot create {destdir}")
                raise Exception(f"run_templates(): source dir {srcdir} does not exist; cannot create {destdir}")
        for root, _, files in os.walk(srcdir):
            for some_file in files:
                # with open('os_walk.tmp', 'a') as debugfile2:
                #     debugfile2.write(f"Srcdir {srcdir}, root {root}, file {some_file}\n")
                excluded = False
                if 'exclude' in self.config:
                    for pattern in self.config['exclude']:
                        if some_file == pattern or re.search(pattern, some_file):
                            # logging.warning(f"some_file {some_file} matches exclusion pattern {pattern}")
                            excluded = True
                            break
                        # else:
                        #     logging.warning(f"some_file {some_file} does not match exclusion pattern {pattern}")
                if excluded:
                    continue
                self.run_file(some_file, destdir, srcdir, root)
    def run_file(self, some_file, destdir, srcdir, root):
        filename_transforms={} # TODO
        config = self.config
        common_path = os.path.commonpath([srcdir, root])
        # raw_relative_path = root.replace(common_path, '')
        relative_path = re.sub('^/', '', root.replace(common_path, ''))
        # logging.info(f"run_templates(): some_file {some_file} (root {root}, relative_path {relative_path})")
        # with open('farts', 'w') as destfh:
        #     destfh.write(f"run_templates(): some_file {some_file} (root {root}, relative_path {relative_path})\n")
        #     destfh.write(f"run_templates(): common_path {common_path}, relative_path {relative_path}\n")
        srcf = os.path.join(srcdir, relative_path, some_file)
        destf = os.path.join(destdir, relative_path, some_file)
        # logger.info(f"run_templates(): from {srcf} to {destf}")
        for from_, to_ in filename_transforms.items():
            # destf0 = destf # DEBUG
            destf = re.sub(from_, to_, destf)
            # logger.info(f"run_templates(): destf before {destf0}, after {destf}, from {from_}, to {to_}") # DEBUG
        os.makedirs(os.path.dirname(destf), exist_ok=True)
        # self.run_template_file(srcf, destf, config)
        # logging.warning(f"Running template file {srcf}")
        self.run_template_file(srcf, destf)

    def run_template_file(self, source_f, dest_f, data=None):
        if data is None:
            if 'data' in self.config:
                data = self.config['data']
            else:
                data = self.config
        with open(source_f, 'r') as srcfh:
            with open(dest_f, 'w') as destfh:
                destfh.write(chevron.render(srcfh, data).replace('<mustache/>','{{'))
