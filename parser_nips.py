# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import os
import urllib.request
from time import sleep

import requests
from tqdm import tqdm

from util import bib_add_item, get_html_content


def parse_nips(args):
    # Config
    BASE_URL = 'http://papers.nips.cc'

    # Check year
    assert 1987 <= args.year <= datetime.datetime.now().year, "Year error"

    # Make dirs
    os.makedirs(args.cache_dir, exist_ok=True)
    os.makedirs(os.path.join(args.cache_dir, args.full_name, 'paper'), exist_ok=True)  # Cache
    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(os.path.join(args.save_dir, 'pdf_{}'.format(args.full_name)), exist_ok=True)  # PDF

    # Get index page
    if args.year == 1987:
        index_url = "neural-information-processing-systems-1987"
    else:
        index_url = "advances-in-neural-information-processing-systems-{}-{}".format(args.year - 1987, args.year)

    print("Get index page...")
    data = get_html_content(os.path.join(BASE_URL, "book", index_url),
                            os.path.join(args.cache_dir, '{}.html'.format(args.full_name)))
    data = data.find("div", class_="main-container").find_all('li')

    # Get papers
    with open(os.path.join(args.save_dir, "{}.bib".format(args.full_name)), 'w') as f:
        for one_paper in tqdm(data):
            try:
                detail_page = one_paper.a['href'].strip().strip('/')
                one_detail = get_html_content(os.path.join(BASE_URL, detail_page),
                                              os.path.join(args.cache_dir, '{}'.format(args.full_name),
                                                           detail_page + ".html"))
                main_content = one_detail.find("div", class_="main")

                # Get bib
                bib = main_content.find('a', text=["[BibTeX]"])['href'].strip().strip('/')
                bib_url = os.path.join(BASE_URL, bib)
                bib_data = requests.get(bib_url, timeout=10, allow_redirects=True).text.strip()

                # Get abstract
                if args.abstract:
                    abstract = one_detail.find('p', class_="abstract").text.strip()
                    if abstract != "Abstract Missing":
                        bib_data = bib_add_item(bib_data, 'abstract', abstract)

                # Get pdf
                if args.pdf:
                    try:
                        pdf = main_content.find('a', text=["[PDF]"])['href'].strip('/')
                        pdf_filename = os.path.split(pdf)[-1]
                        pdf_url = os.path.join(BASE_URL, pdf)
                        pdf_path = os.path.join('pdf_{}'.format(args.full_name), pdf_filename)
                        bib_data = bib_add_item(
                            bib_data, 'file', "{}:{}:application/pdf".format(pdf_filename, pdf_path))
                        pdf_path = os.path.join(args.save_dir, pdf_path)
                        if not os.path.exists(pdf_path):
                            urllib.request.urlretrieve(pdf_url, pdf_path)
                            sleep(args.pdf_sleep)
                    except Exception as e:
                        print(one_paper.a.text)
                        print(e)

                # Save
                f.write(bib_data + "\n")
                tqdm.write(one_paper.a.text)

            except Exception as e:
                print(e)
