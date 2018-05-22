# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from time import sleep

import requests
from bs4 import BeautifulSoup


def get_html_content(url, cache=None, sleep_time=1):
    if cache and os.path.exists(cache):
        with open(cache, "r") as f:
            data_txt = f.read()
    else:
        response = requests.get(url, timeout=10, allow_redirects=True)
        data_txt = response.text
        if cache:
            with open(cache, "w") as f:
                f.write(data_txt)
        if sleep_time > 0:
            sleep(sleep_time)

    return BeautifulSoup(data_txt, "html5lib")
