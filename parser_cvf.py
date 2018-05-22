# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import urllib.request
from time import sleep

from tqdm import tqdm

from util import bib_add_item, get_html_content


def parse_cvf(args):
    # Config
    BASE_URL = 'http://openaccess.thecvf.com/'

    # Make dirs
    os.makedirs(os.path.join(args.cache_dir, args.full_name), exist_ok=True)  # Cache
    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(os.path.join(args.save_dir, 'pdf_{}'.format(args.full_name)), exist_ok=True)  # PDF

    print("Get index page...")
    data = get_html_content(
        os.path.join(BASE_URL, args.full_name + ".py"),
        os.path.join(args.cache_dir, args.full_name + ".html"))

    jar_abs = data.find_all(attrs={'class': 'ptitle'})
    jar_bib = data.find_all(attrs={'class': 'bibref'})
    jar_pdf = data.find_all('a', text=["pdf"])

    with open(os.path.join(args.save_dir, "{}.bib".format(args.full_name)), 'w') as f:
        for paper_url, bib_data, pdf_url in tqdm(zip(jar_abs, jar_bib, jar_pdf)):

            # Get bib
            bib_data = bib_data.text.replace('<br>', "").strip()

            # Get abstract
            if args.abstract:
                try:
                    abstract_url = os.path.join(BASE_URL, paper_url.a['href'])
                    abstract_path = os.path.join(
                        args.cache_dir, args.full_name, os.path.split(abstract_url)[-1])
                    abstract_html = get_html_content(abstract_url, abstract_path)
                    abstract = abstract_html.find(id="abstract").text
                    bib_data = bib_add_item(bib_data, "abstract", abstract, pos=-2)
                except Exception as e:
                    print(paper_url.a.text)
                    print(e)

            # Get pdf
            pdf_url = os.path.join(BASE_URL, pdf_url['href'])
            pdf_filename = os.path.split(pdf_url)[-1]
            pdf_path = os.path.join('pdf_{}'.format(args.full_name), pdf_filename)
            bib_data = bib_add_item(bib_data, 'url', pdf_url, pos=-2)
            if args.pdf:
                try:
                    bib_data = bib_add_item(
                        bib_data, 'file', "{}:{}:application/pdf".format(pdf_filename, pdf_path), pos=-2)
                    pdf_path = os.path.join(args.save_dir, pdf_path)
                    if not os.path.exists(pdf_path):
                        urllib.request.urlretrieve(pdf_url, pdf_path)
                        sleep(args.pdf_sleep)
                except Exception as e:
                    print(paper_url.a.text)
                    print(e)

            # Save
            f.write(bib_data + "\n")
            tqdm.write(paper_url.a.text)
