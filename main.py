# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from argparse import ArgumentParser

from easydict import EasyDict

from parser_cvf import parse_cvf
from parser_iclr import parse_iclr
from parser_nips import parse_nips

config = EasyDict(
    save_dir="RESULT",
    cache_dir="cache",
    url_sleep=1,
    pdf_sleep=5
)

PARSERS = {
    "CVPR": parse_cvf,
    "ICCV": parse_cvf,
    "ECCV": parse_cvf,
    "NIPS": parse_nips,
    "ICLR": parse_iclr,
}


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('name', type=str, help='Name')
    parser.add_argument('year', type=int, help='Year')
    parser.add_argument('-a', '--abstract', action='store_true',
                        help='Download abstract.')
    parser.add_argument('-p', '--pdf', action='store_true',
                        help='Download pdf file. DO NOT DO THIS IF NOT NECESSARY.')
    return parser.parse_args()


def main(args):
    args.name = args.name.strip().upper()
    assert args.name in PARSERS, "Unknown name {}".format(args.name)

    args = EasyDict(**config, **args.__dict__)
    args.full_name = "{}{}".format(args.name, args.year)
    PARSERS[args.name](args)


if "__main__" == __name__:
    args = parse_args()
    main(args)
