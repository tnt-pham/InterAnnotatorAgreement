# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 09-Jun-2021
# Python 3.7
# Windows 10
"""Command line manager."""

import argparse
import logging
import sys

from annotation import Annotation
from errors import DifferentTextException
from filetostring import FileToString
from interannotatoragreement import InterAnnotatorAgreement


logging.basicConfig(filename="interannotatoragreement_log.log",
                    level=logging.INFO,
                    format="%(levelname)s:%(asctime)s:%(message)s")


def configure_parser():
    """Argument structure configuration for command line."""
    parser = argparse.ArgumentParser(description="InterAnnotatorAgreement"
                                                 " (IAA) tool."
                                                 " How similar are your"
                                                 " markable annotations?",
                                     epilog="The Readme and your logfile"
                                            " interannotatoragreement_log.log"
                                            " may also provide some helpful"
                                            " information, especially on how"
                                            " to annotate the texts."
                                            " Have fun!")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--text",
                       nargs=2,
                       metavar="TEXT",
                       help="Two text annotations to be compared."
                            " Need to be the same texts.")
    group.add_argument("-f", "--file",
                       nargs=2,
                       metavar="FILE",
                       help="Two files, with text annotations to be compared."
                            " Need to be the same texts.")

    parser.add_argument("--naive",
                        action="store_true",
                        help="Naive similarity metric: What is the agreement"
                             " of having annotated a markable or not?")
    parser.add_argument("--ngram",
                        action="store_true",
                        help="NGram similarity metric: How well do markable"
                             " boundaries agree?")
    parser.add_argument("--levenshtein",
                        action="store_true",
                        help="Levenshtein distance: How many changes are"
                             " needed until both annotations are equal?"
                             " Normalized: How many changes are needed"
                             " per markable (on average)?")

    parser.add_argument("--encoding",
                        nargs=1,
                        default=["utf-8"],
                        metavar="ENC",
                        help="Encoding for both files. Defaults to utf-8.")
    parser.add_argument("--opening",
                        nargs=1,
                        default=["["],
                        metavar="BRACKET",
                        help="Opening bracket used for annotation.")
    parser.add_argument("--closing",
                        nargs=1,
                        default=["]"],
                        metavar="BRACKET",
                        help="Closing bracket used for annotation.")
    return parser


def command_line_execution(args):
    """Manages interaction between command line and InterAnnotatorAgreement."""
    if args.text:
        text1, text2 = args.text
    elif args.file:
        try:
            text1 = FileToString(args.file[0], args.encoding[0]).text
            text2 = FileToString(args.file[1], args.encoding[0]).text
        except (FileNotFoundError, PermissionError):
            logging.error(sys.exc_info()[1])
            parser.error(sys.exc_info()[1])
    else:
        parser.error("Missing argument: --text TEXT TEXT or --file FILE FILE\n"
                     "Please specify the annotated texts to be compared."
                     " You may find help with '--help'.")
    try:
        ao1 = Annotation(text1, opening_bracket=args.opening[0],
                         closing_bracket=args.closing[0])
        ao2 = Annotation(text2, opening_bracket=args.opening[0],
                         closing_bracket=args.closing[0])
    except ValueError:
        logging.error(sys.exc_info()[1])
        parser.error(sys.exc_info()[1])
    try:
        iaa = InterAnnotatorAgreement(ao1, ao2)
    except DifferentTextException:
        logging.error(sys.exc_info()[1])
        parser.error(sys.exc_info()[1])
    if args.naive:
        print("Naive Accuracy:", iaa.naive_accuracy())
    if args.ngram:
        print("NGram Accuracy:", iaa.mean_ngreement())
    if args.levenshtein:
        dist, dist_normalized = iaa.levenshtein_incl_normalized()
        print(f"Levenshtein Distance: {dist}\n"
              f"Normalized Levenshtein: {dist_normalized}")
    if not(args.naive or args.ngram or args.levenshtein):
        parser.error("Missing argument: --naive or --ngram or --levenshtein\n"
                     "Please choose depending on which metric(s) you want to"
                     " deploy for the two text annotations.")


if __name__ == "__main__":
    parser = configure_parser()
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        command_line_execution(args)
