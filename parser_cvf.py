# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import urllib.request
from time import sleep

import bibtexparser
from tqdm import tqdm

from util import get_html_content


def parse_cvf(args):
    # Config
    BASE_URL = 'http://openaccess.thecvf.com'

    # Make dirs
    os.makedirs(os.path.join(args.cache_dir, args.full_name), exist_ok=True)  # Cache
    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(os.path.join(args.save_dir, 'pdf_{}'.format(args.full_name)), exist_ok=True)  # PDF

    url_list = []
    if args.year >= 2018:
        data = get_html_content(
            os.path.join(BASE_URL, args.full_name + ".py"),
            os.path.join(args.cache_dir, args.full_name + ".html"))
        sub_pages = data.find_all("a", text=lambda x: x and x.startswith("Day"))
        for sub_url in sub_pages:
            url_list.append((f"{BASE_URL}/{sub_url['href']}",
                             os.path.join(args.cache_dir, sub_url['href'] + ".html")))
    else:
        url_list.append((f"{BASE_URL}/{args.full_name}.py",
                         os.path.join(args.cache_dir, args.full_name + ".html")))

    with open(os.path.join(args.save_dir, "{}.bib".format(args.full_name)), 'w') as f:
        for item in url_list:
            print("Get index page...")
            data = get_html_content(*item)

            jar_abs = data.find_all(attrs={'class': 'ptitle'})
            jar_bib = data.find_all(attrs={'class': 'bibref'})
            jar_pdf = data.find_all('a', text=["pdf"])

            for paper_url, bib_data, pdf_url in tqdm(zip(jar_abs, jar_bib, jar_pdf)):

                # Get bib
                bib_data = bibtexparser.loads(bib_data.text.replace('<br>', "").strip())

                # Get abstract
                if args.abstract:
                    try:
                        abstract_url = os.path.join(BASE_URL, paper_url.a['href'])
                        abstract_path = os.path.join(
                            args.cache_dir, args.full_name, os.path.split(abstract_url)[-1])
                        abstract_html = get_html_content(abstract_url, abstract_path)
                        abstract = abstract_html.find(id="abstract").text.strip()
                        bib_data.entries[0]["abstract"] = abstract
                    except Exception as e:
                        print(paper_url.a.text)
                        print(e)

                # Get pdf
                pdf_url = os.path.join(BASE_URL, pdf_url['href'])
                pdf_filename = os.path.split(pdf_url)[-1]
                pdf_path = os.path.join('pdf_{}'.format(args.full_name), pdf_filename)
                bib_data.entries[0]["url"] = pdf_url
                if args.pdf:
                    try:
                        bib_data.entries[0]["file"] = "{}:{}:application/pdf".format(pdf_filename, pdf_path)
                        pdf_path = os.path.join(args.save_dir, pdf_path)
                        if not os.path.exists(pdf_path):
                            urllib.request.urlretrieve(pdf_url, pdf_path)
                            sleep(args.pdf_sleep)
                    except Exception as e:
                        print(paper_url.a.text)
                        print(e)

                # Save
                f.write(bibtexparser.dumps(bib_data))
                tqdm.write(paper_url.a.text)
