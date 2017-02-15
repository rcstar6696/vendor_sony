#!/usr/bin/env python

import re
import os
import sys
from string import Template

worklist = [
    ('etc', 'Sony Mobile', 'ETC', '$(TARGET_OUT)'),
    ('vendor/bin', 'Sony Mobile', 'EXECUTABLES', '$(TARGET_OUT)'),
    ('vendor/etc', 'Sony Mobile', 'ETC',  '$(TARGET_OUT)'),
    ('vendor/firmware', 'Sony Mobile', 'ETC',  '$(TARGET_OUT)'),
    ('vendor/lib', 'Sony Mobile', 'SHARED_LIBRARIES',  '$(TARGET_OUT)'),
]


#
# replace_in_file
#
# replace the section in between the two strings start and
# end with the text text
#
def replace_in_file(path, start, end, text):
    try:
        with open(path, 'r') as f:
            content = f.read()

        head = content[:content.index(start) + len(start)]
        if end:
            tail = content[content.index(end):]
        else:
            tail = ""

        content = "\n".join([head, text, tail])

        with open(path, 'w') as f:
            f.write(content)

    except IOError, err:
        print err
        sys.exit(1)

#
# list_files
#
# generate a sorted list of all files in a directory
#
def list_files(path, relpath):
    files = [os.path.join(subdir, f) for (subdir, dirs, files) in os.walk(path) for f in files]
    if relpath:
        files = [os.path.relpath(f, relpath) for f in files]
    return sorted(files)

#
# generate_module
#
# create a module object from a file name and parameters
#
def generate_module(f, owner, modclass, target_base):
    name = os.path.basename(f)
    stem, suffix = os.path.splitext(name)

    mod = {}
    mod['files'] = f
    mod['owner'] = owner
    mod['module'] = name.replace('.', '_')
    mod['stem'] = stem
    mod['suffix'] = suffix
    if suffix == '.so' :
        mod['class'] = 'SHARED_LIBRARIES'
    else :
        mod['class'] = modclass
    mod['target_base'] = target_base
    mod['target_path'] = os.path.dirname(f)
    return mod

#
# module_definition
#
# turn a mod into a text represenatation that define that module
#
def module_definition_for_colision(mod):
    module_template = Template(
    '''include $$(CLEAR_VARS)
LOCAL_MODULE := $module
LOCAL_MODULE_OWNER := $owner
LOCAL_SRC_FILES := $files
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_STEM := $stem
LOCAL_MODULE_SUFFIX := $suffix
LOCAL_MODULE_CLASS := $class
LOCAL_MODULE_PATH := $target_base/$target_path
include $$(BUILD_PREBUILT)''')
    return module_template.substitute(mod)

def module_definition(mod):
    module_template = Template(
    '''include $$(CLEAR_VARS)
LOCAL_MODULE := $stem
LOCAL_MODULE_OWNER := $owner
LOCAL_SRC_FILES := $files
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := $suffix
LOCAL_MODULE_CLASS := $class
LOCAL_MODULE_PATH := $target_base/$target_path
include $$(BUILD_PREBUILT)''')
    return module_template.substitute(mod)

module_list = []
for work in worklist:
    files = list_files(os.path.join('proprietary', work[0]), 'proprietary')
    module_list += [generate_module(f, work[1], work[2], work[3]) for f in files]

module_count = {}
for module in module_list:
    if not module['stem'] in module_count:
        module_count[module['stem']] = 0
    module_count[module['stem']] += 1

definitions = []
packages = []
for module in module_list:
    if module_count[module['stem']] > 1:
        definitions.append(module_definition_for_colision(module))
        packages.append(module['module'])
    else:
        definitions.append(module_definition(module))
        packages.append(module['stem'])

definitions = "\n\n".join(definitions)
packages = "\t" + " \\\n\t".join(packages)

replace_in_file('proprietary/Android.mk', '$(TARGET_DEVICE))', 'endif', definitions)
replace_in_file('kagura-partial.mk', 'PRODUCT_PACKAGES += \\', None, packages)

