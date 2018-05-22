# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import urllib.request
from argparse import ArgumentParser
from time import sleep

from tqdm import tqdm

from common import bib_add_item, get_html_content

BASE_URL = 'http://openaccess.thecvf.com/'
SAVE_DIR = "RESULT"
CACHE_DIR = "cache"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('name', default='CVPR2017', help='Year')
    parser.add_argument('-a', '--abstract', action='store_true',
                        help='Download abstract.')
    parser.add_argument('-p', '--pdf', action='store_true',
                        help='Download pdf file. DO NOT DO THIS IF NOT NECESSARY.')
    return parser.parse_args()


def main(args):
    # Make dirs
    os.makedirs(os.path.join(CACHE_DIR, args.name), exist_ok=True)  # Cache
    os.makedirs(SAVE_DIR, exist_ok=True)
    os.makedirs(os.path.join(SAVE_DIR, 'pdf_{}'.format(args.name)),
                exist_ok=True)  # PDF

    print("Get index page...")
    data = get_html_content(
        os.path.join(BASE_URL, args.name + ".py"),
        os.path.join(CACHE_DIR, args.name + ".html"))

    jar_abs = data.find_all(attrs={'class': 'ptitle'})
    jar_bib = data.find_all(attrs={'class': 'bibref'})
    jar_pdf = data.find_all('a', text=["pdf"])

    with open(os.path.join(SAVE_DIR, "{}.bib".format(args.name)), 'w') as f:
        for paper_url, bib_data, pdf_url in tqdm(zip(jar_abs, jar_bib, jar_pdf)):

            # Get bib
            bib_data = bib_data.text.replace('<br>', "").strip()

            # Get abstract
            if args.abstract:
                try:
                    abstract_url = os.path.join(BASE_URL, paper_url.a['href'])
                    abstract_path = os.path.join(
                        CACHE_DIR, args.name, os.path.split(abstract_url)[-1])
                    abstract_html = get_html_content(
                        abstract_url, abstract_path)
                    abstract = abstract_html.find(id="abstract").text
                    bib_data = bib_add_item(
                        bib_data, "abstract", abstract, pos=-2)
                except Exception as e:
                    print(paper_url.a.text)
                    print(e)

            # Get pdf
            pdf_url = os.path.join(BASE_URL, pdf_url['href'])
            pdf_filename = os.path.split(pdf_url)[-1]
            pdf_path = os.path.join('pdf_{}'.format(args.name), pdf_filename)
            bib_data = bib_add_item(
                bib_data, 'url', pdf_url, pos=-2)
            if args.pdf:
                try:
                    bib_data = bib_add_item(
                        bib_data, 'file', "{}:{}:application/pdf".format(pdf_filename, pdf_path), pos=-2)
                    pdf_path = os.path.join(SAVE_DIR, pdf_path)
                    if not os.path.exists(pdf_path):
                        urllib.request.urlretrieve(pdf_url, pdf_path)
                        sleep(5)
                except Exception as e:
                    print(paper_url.a.text)
                    print(e)

            # Save
            f.write(bib_data + "\n")
            tqdm.write(paper_url.a.text)


if '__main__' == __name__:
    args = parse_args()
    args.name = args.name.upper().strip()
    main(args)
