#!/bin/env python3
import os
import sys
import fnmatch
import argparse
import yaml
import re
from jinja2 import Environment,FileSystemLoader,Template

def parse_options(argv):
    script_dir=os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--explain", help="render explain queries",
                        action="store_true")
    parser.add_argument("-t", "--templates_dir", help="directory holding tpch query templates",
                        default="{}/../templates".format(script_dir))
    parser.add_argument("-f", "--vars_file", help="file containing jinja2 variables")
    parser.add_argument("-o", "--output_dir", help="directory to store rendered queries",
                        default="{}/../queries".format(script_dir))
    args = parser.parse_args(argv)
    return args

def get_level(path):
    regex = re.compile(r"/")
    level = len(regex.findall(path))
    return level

def get_dirs(templates_dir):
    paths = [templates_dir]
    for root, dirs, files in os.walk(templates_dir):
        for dname in dirs:
            paths.append(os.path.join(root, dname))
    return paths

def get_variables(vname, levels, level):
    variables = {}
    for l in range(0, level):
        try:
            variables.update(levels[l])
        except KeyError as e:
            continue
    try:
        with open(vname) as vars_file:
            variables.update(yaml.load(vars_file))
    except OSError as e:
        pass
    return variables

def main(argv):
    args = parse_options(argv)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    levels = {}
    variables = {}

    if args.vars_file is not None:
        base_level = 0
        variables = get_variables(args.vars_file, levels, base_level)
        levels[base_level] = variables

    for dname in get_dirs(args.templates_dir):
        level = get_level(dname)
        variables = get_variables("{}/vars.yml".format(dname), levels, level)
        levels[level] = variables
        j2env = Environment(loader=FileSystemLoader(dname),
                            trim_blocks=True)
        templates = os.listdir(dname)
        for t in templates:
            if fnmatch.fnmatch(t, "*.j2"):
                template = j2env.get_template(t)
                query_filepath = "{}/{}".format(args.output_dir, t[:-3])
                with open(query_filepath, "w") as f:
                    query_content = template.render(variables=variables, explain=args.explain)
                    f.write(query_content)

if __name__ == "__main__":
    main(sys.argv[1:])
