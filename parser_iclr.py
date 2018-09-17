# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import urllib.request
from time import sleep

import bibtexparser
from tqdm import tqdm

from util import get_html_content


def parse_iclr(args):
    # Config
    BASE_URL = 'https://iclr.cc/Conferences/{}/Schedule'.format(args.year)
    CONFERENCE_NAME = "International Conference on Learning Representations (ICLR)"

    # Make dirs
    os.makedirs(os.path.join(args.cache_dir, args.full_name), exist_ok=True)  # Cache
    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(os.path.join(args.save_dir, 'pdf_{}'.format(args.full_name)), exist_ok=True)  # PDF

    print("Get index page...")
    data = get_html_content(
        os.path.join(BASE_URL),
        os.path.join(args.cache_dir, args.full_name + ".html"))

    jar_paper = data.find_all(class_=re.compile("maincard narrower (Oral|Poster)"))

    with open(os.path.join(args.save_dir, "{}.bib".format(args.full_name)), 'w') as f:
        for paper in tqdm(jar_paper):
            paper_name = paper.find("div", class_="maincardBody").text
            paper_url = paper.find("a", class_="href_PDF")['href']
            pdf_url = paper_url.replace("forum?id=", "pdf?id=")
            paper_data = get_html_content(
                paper_url, os.path.join(args.cache_dir, args.full_name, paper_url.split("=")[-1]) + ".html")

            # Get bib
            bib_data = paper_data.find("a", class_="action-bibtex-modal")["data-bibtex"]
            bib_data = bibtexparser.loads(bib_data)
            bib_data.entries[0]["url"] = pdf_url
            bib_data.entries[0]["booktitle"] = CONFERENCE_NAME

            # Get abstract
            if args.abstract:
                try:
                    abstract = paper_data.find("span", class_="note-content-value").text.replace("\n", "")
                    bib_data.entries[0]["abstract"] = abstract
                except Exception as e:
                    print(paper_name)
                    print(e)

            # Get pdf
            if args.pdf:
                try:
                    pdf_filename = pdf_url.split("id=")[-1]
                    pdf_path = os.path.join('pdf_{}'.format(args.full_name), pdf_filename)
                    bib_data.entries[0]["file"] = "{}:{}:application/pdf".format(pdf_filename, pdf_path)
                    if not os.path.exists(pdf_path):
                        urllib.request.urlretrieve(pdf_url, pdf_path)
                        sleep(args.pdf_sleep)
                except Exception as e:
                    print(paper_name)
                    print(e)

            # Save
            f.write(bibtexparser.dumps(bib_data))
            tqdm.write(paper_name)
