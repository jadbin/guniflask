# coding=utf-8

from flask import render_template

from guniflask.config.template import _template_folder
from guniflask.web import blueprint, get_route


@blueprint('/hello-world', template_folder=_template_folder)
class HelloWorld:
    @get_route('/')
    def home_page(self):
        """
        Home page
        """
        return render_template('hello_world/index.html')
