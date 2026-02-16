###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import wmo_sphinx_theme

project = 'CAP Composer'
author = 'World Meteorological Organization (WMO)'
license = 'This work is licensed under a Creative Commons Attribution 4.0 International License'  # noqa
copyright = '2021-2025, ' + author + ' ' + license

# TO DO, figure out how to get version from package
release = 'latest'

templates_path = ['_templates']

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

today_fmt = '%Y-%m-%d'

html_theme = 'wmo_sphinx_theme'
html_theme_path = wmo_sphinx_theme.get_html_theme_path()
html_css_files = [
    'wmo.css'
]
html_static_path = ['_static']

html_favicon = '_static/favicon.ico'
html_logo = '_static/logo.png'

linkcheck_ignore = [
    r'http://localhost:\d+/'
]
