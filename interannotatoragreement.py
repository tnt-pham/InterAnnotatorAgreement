# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 03-Jun-2021
# Python 3.7
# Windows 10
"""Ascertains similarity between two Annotation objects."""

from nltk.tokenize import word_tokenize
import re

from annotation import Annotation
from errors import DifferentTextException


class InterAnnotatorAgreement:
    def __init__(self, annotation_obj1, annotation_obj2):
        if len(annotation_obj1.text_split) != len(annotation_obj2.text_split):
            raise DifferentTextException("Two Annotation objects are not compatible. Check the annotation guidelines please.")  # how to set brackets

        self.ao1 = annotation_obj1
        self.ao2 = annotation_obj2

    def count_agreement(self):
        same_in_bracket_count = len(self.ao1.annotated_indices.intersection(self.ao2.annotated_indices))
        disagree_count = len(self.ao1.annotated_indices.union(self.ao2.annotated_indices)) - same_in_bracket_count
        same_not_bracket_count = len(self.ao1.text_split) - same_in_bracket_count - disagree_count
        return same_in_bracket_count, same_not_bracket_count, disagree_count

    def naive_accuracy(self):
        same_in_bracket_count, same_not_bracket_count, disagree_count = self.count_agreement()
        return (same_in_bracket_count + same_not_bracket_count)/(same_in_bracket_count + same_not_bracket_count + disagree_count)

    def ngram_score(self):
        counter = 0
        subgrams = []

    @staticmethod
    def get_subgrams(ngram_indices):  # z.B. [4, 5, 6, 7]
        subgrams = []
        for i in range(len(ngram_indices), 0, -1):  # shortens list from the right hand side  # 4, 3, 2, 1
            for j in range(i):  # shortens list from the left hand side  # 0, 1, 2, 3 // 0, 1, 2 // 0, 1 // 0
                subgrams.append(ngram_indices[j:i])
        return subgrams  # [[4, 5, 6, 7], [5, 6, 7], [6, 7], [7], [4, 5, 6], [5, 6], [6], [4, 5], [5], [4]]


def find_context(text):
    pattern = r"\w*\s*\[.+?\]\s*\w*"
    return re.findall(pattern, text)


def find_markables(text):
    pattern = r"\[.+?\]"
    return re.findall(pattern, text)


if __name__ == "__main__":
    data1 = "[Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    data2 = "[Er] geht zu Lisa. [Niemand] hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich den großen [Raum], als [Peter] seinen [Mund] öffnete."
    # what about [der] [große] [Raum]

    # print("mit nltk word_tokenize:\n", word_tokenize(data1))
    # print("mit split:\n", data1.split())

    # markables_iter = naive_find_markables(data1)
    # for markable in markables_iter:
    #     print(markable.span())

    ao1 = Annotation(data1)
    ao2 = Annotation(data2)
    iaa = InterAnnotatorAgreement(ao1, ao2)
    agree_markable, agree_nonmarkable, disagree = iaa.count_agreement()
    print(f"agree markable: {agree_markable}\nagree non-markable: {agree_nonmarkable}\ndisagree: {disagree}")
    print("Accuracy:", iaa.naive_accuracy())

    print(iaa.ao1.annotated_indices_groups)
    print(iaa.get_subgrams([4, 5, 6, 7]))
    print(find_markables(data1))

