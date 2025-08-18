#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: 1058449090@qq.com

import os
import yaml
from jinja2 import Environment as jjEnvironment
from jinja2 import FileSystemLoader as jjFileSystemLoader


class YamlRender(object):
    def __init__(self, config_file, template_dir='template', render_dir='render'):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.__config = yaml.full_load(f.read())

        self.__jjenv = jjEnvironment(loader=jjFileSystemLoader(template_dir))
        self.__templates = list()

        self.__render_dir = render_dir
        if not os.path.exists(render_dir):
            os.makedirs(render_dir)

    def __get_template_list(self):
        """
        找出模板目录中所有的 yaml/yml 文件
        :return:
        """
        for item in self.__jjenv.list_templates():
            if item.endswith('.yml') or item.endswith('.yaml'):
                self.__templates.append(item)
        # print(self.__templates)
        return True

    def __render(self, template_file):
        """
        渲染模板生成可部署的 YAML 文件
        :param template_file:
        :return:
        """
        print('Render template: %s' % template_file)
        render_file = os.path.join(self.__render_dir, template_file)
        render_file_dir = os.path.split(render_file)[0]
        if not os.path.exists(render_file_dir):
            os.makedirs(render_file_dir)
        content = self.__jjenv.get_template(template_file).render(self.__config)
        with open(render_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('\tSucceed to generate %s' % render_file)
        return True

    def render_all(self):
        """
        渲染所有的模板
        :return:
        """
        self.__get_template_list()
        for tmpl in self.__templates:
            self.__render(tmpl)
        print('\nComplete all')
        return True


if __name__ == '__main__':
    print('This is Python scripts')
