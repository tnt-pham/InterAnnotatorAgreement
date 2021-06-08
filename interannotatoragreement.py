# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 03-Jun-2021
# Python 3.7
# Windows 10
"""Ascertains similarity between two Annotation objects."""

import re

from annotation import Annotation
from errors import DifferentTextException


class InterAnnotatorAgreement:  # or rather IAA
    def __init__(self, annotation_obj1, annotation_obj2):
        if len(annotation_obj1.text_split) != len(annotation_obj2.text_split):
            raise DifferentTextException("Two Annotation objects are not compatible. Please check the annotation guidelines.")  # how to set brackets

        self.ao1 = annotation_obj1
        self.ao2 = annotation_obj2

    def naive_count_agreement(self):
        same_in_bracket_count = len(self.ao1.annotated_indices.intersection(self.ao2.annotated_indices))
        disagree_count = len(self.ao1.annotated_indices.union(self.ao2.annotated_indices)) - same_in_bracket_count
        same_not_bracket_count = len(self.ao1.text_split) - same_in_bracket_count - disagree_count
        return same_in_bracket_count, same_not_bracket_count, disagree_count

    def naive_accuracy(self):
        same_in_bracket_count, same_not_bracket_count, disagree_count = self.naive_count_agreement()
        return (same_in_bracket_count + same_not_bracket_count)/(same_in_bracket_count + same_not_bracket_count + disagree_count)

    def ngram_accuracy(self, indice_groups_ref, indice_groups_comp, n=2):
        """Ascertains how well an annotation is compatible with a reference by...
        Distance is not symmetric
        NGreement (haha)
        """
        max_score = 0
        score = 0
        subgrams = []  # to be filled with lists of lists of indices
        for group in indice_groups_ref:
            subgrams.append(self.get_subgrams(group))
            max_score += len(group)**n
        for group in indice_groups_comp:
            # first elem is always the largest group with every index
            for subgrams_list in subgrams:
                # compare both smallest indices
                if group[0] < subgrams_list[0][0]:
                    break  # because indices in subgrams only get higher
                if group[0] not in subgrams_list[0]:
                    continue
                if group in subgrams_list:
                    score += len(group)**n
                    break
        if max_score == 0:
            return 0
        return score/max_score

    def ngram_mean_accuracy(self, n=2):
        """Limitation: längere Texte (bekommen mit mehr Disagreement weniger Punkte?)"""
        annotated_acc1 = self.ngram_accuracy(self.ao1.annotated_indices_groups, self.ao2.annotated_indices_groups, n=n)
        not_annotated_acc1 = self.ngram_accuracy(self.ao1.not_annotated_indices_groups, self.ao2.not_annotated_indices_groups, n=n)
        annotated_acc2 = self.ngram_accuracy(self.ao2.annotated_indices_groups, self.ao1.annotated_indices_groups, n=n)
        not_annotated_acc2 = self.ngram_accuracy(self.ao2.not_annotated_indices_groups, self.ao1.not_annotated_indices_groups, n=n)
        return annotated_acc1, annotated_acc2, not_annotated_acc1, not_annotated_acc2, "durch 4:", (annotated_acc1 + annotated_acc2 + not_annotated_acc1 + not_annotated_acc2)/4, (annotated_acc1 + not_annotated_acc1)/2, (annotated_acc2 + not_annotated_acc2)/2

    @staticmethod
    def get_subgrams(ngram_indices):  # z.B. [4, 5, 6, 7]
        subgrams = []
        for i in range(len(ngram_indices), 0, -1):  # shortens list from the right hand side  # 4, 3, 2, 1
            for j in range(i):  # shortens list from the left hand side  # 0, 1, 2, 3 // 0, 1, 2 // 0, 1 // 0
                subgrams.append(ngram_indices[j:i])
        return subgrams  # [[4, 5, 6, 7], [5, 6, 7], [6, 7], [7], [4, 5, 6], [5, 6], [6], [4, 5], [5], [4]]

    def levenshtein(self, indices_groups_ref, indices_groups_comp):
        """How many changes until comp looks like ref?"""
        # base cases
        if len(indices_groups_ref) == 0 and len(indices_groups_comp) == 0:
            return 0
        if len(indices_groups_ref) == 0:
            return len(indices_groups_comp)  # missing groups
        if len(indices_groups_comp) == 0:
            return len(indices_groups_ref)  # missing groups

        # recursive cases
        if indices_groups_ref[0] == indices_groups_comp[0]:
            return self.levenshtein(indices_groups_ref[1:], indices_groups_comp[1:])
        else:  # not the same
            if self.is_compatible(indices_groups_ref[0], indices_groups_comp[0]):
                # until this index, groups in comp can be transformed to ref
                compatible_index_boundary_in_ref = self.find_compatible_index_boundary(indices_groups_comp[0], indices_groups_ref)  # new
                compatible_index_boundary_in_comp = self.find_compatible_index_boundary(indices_groups_ref[0], indices_groups_comp)

                if compatible_index_boundary_in_ref < compatible_index_boundary_in_comp:  # new
                    return self.transform_groups_cost(indices_groups_ref[0], indices_groups_comp[:compatible_index_boundary_in_comp]) + self.levenshtein(indices_groups_ref[1:], indices_groups_comp[compatible_index_boundary_in_comp:])
                else:  # new
                    return self.transform_groups_cost(indices_groups_comp[0], indices_groups_ref[:compatible_index_boundary_in_ref]) + self.levenshtein(indices_groups_ref[compatible_index_boundary_in_ref:], indices_groups_comp[1:])

            else:  # first groups disagree completely
                # first ref group is missing
                if indices_groups_ref[0][0] < indices_groups_comp[0][0]:
                    return 1 + self.levenshtein(indices_groups_ref[1:], indices_groups_comp)
                else:  # first comp group is too much
                    return 1 + self.levenshtein(indices_groups_ref, indices_groups_comp[1:])

    @staticmethod
    def transform_groups_cost(group_ref, indices_groups_comp):
        set_ref = set(group_ref)
        set_comp = set()
        for group in indices_groups_comp:
            set_comp.update(set(group))
        add_delete_cost = len(set_ref.symmetric_difference(set_comp))
        merge_cost = len(indices_groups_comp) - 1
        return add_delete_cost + merge_cost

    @staticmethod
    def is_compatible(group_ref, group_comp):
        set_ref = set(group_ref)
        set_comp = set(group_comp)
        if len(set_ref.intersection(set_comp)) == 0:
            return False
        return True

    @staticmethod
    def find_index(searchlist, element):
        for num, list_el in enumerate(searchlist):
            if list_el == element:
                return num
        return -1

    @staticmethod
    def find_compatible_index_boundary(group_ref, indices_groups_comp):  # TODO: new argument names
        """Find the index in a group collection until which the groups
        are compatible with the reference group.
        """
        for num1, group in enumerate(indices_groups_comp):
            for num2, index in enumerate(group):
                if index not in group_ref:
                    if num2 == 0:  # whole group already incompatible
                        return num1
                    return num1 + 1  # part of the group compatible
        return num1 + 1


def find_context(text):
    pattern = r"\w*\s*\[.+?\]\s*\w*"
    return re.findall(pattern, text)


def find_markables(text):
    pattern = r"\[.+?\]"
    return re.findall(pattern, text)


if __name__ == "__main__":
    data1 = "[Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    data2 = "[Er] geht zu Lisa. [Niemand] hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    data3 = "[Er geht zu Lisa]. [Niemand hat damit gerechnet, dass Laura dabei sein würde]. [Fatma ist entsetzt]. [Sie verließ augenblicklich den großen Raum], [als Peter seinen Mund öffnete]."
    data4 = "[Er] [geht] [zu] [Lisa]. [Niemand] [hat] [damit] [gerechnet], [dass] [Laura] [dabei] [sein] [würde]. [Fatma] [ist] [entsetzt]. [Sie] [verließ] [augenblicklich] [den] [großen] [Raum], [als] [Peter] [seinen] [Mund] [öffnete]."
    data5 = "[Er] geht zu Lisa. [Niemand hat] damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."

    # print("mit nltk word_tokenize:\n", word_tokenize(data1))
    # print("mit split:\n", data1.split())

    # markables_iter = naive_find_markables(data1)
    # for markable in markables_iter:
    #     print(markable.span())

    ao1 = Annotation(data1)
    ao2 = Annotation(data2)
    iaa = InterAnnotatorAgreement(ao1, ao2)
    agree_markable, agree_nonmarkable, disagree = iaa.naive_count_agreement()
    print(f"agree markable: {agree_markable}\nagree non-markable: {agree_nonmarkable}\ndisagree: {disagree}")
    print("accuracy:", iaa.naive_accuracy())

    print("groups:", iaa.ao1.annotated_indices_groups)
    print("subgrams", iaa.get_subgrams([4, 5, 6, 7]))
    print("markable:", find_markables(data1))
    print(iaa.get_subgrams([5]))
    print(iaa.get_subgrams([5, 2]))

    print("1 und 2:", iaa.ngram_mean_accuracy())

    ao3 = Annotation(data3)
    iaa1_3 = InterAnnotatorAgreement(ao1, ao3)
    print("1 und 3:", iaa1_3.ngram_mean_accuracy())

    iaa1_1 = InterAnnotatorAgreement(ao1, ao1)
    print("1 und 1:", iaa1_1.ngram_mean_accuracy())

    ao4 = Annotation(data4)
    iaa3_4 = InterAnnotatorAgreement(ao3, ao4)
    print("3 und 4:", iaa3_4.ngram_mean_accuracy())
    print(iaa3_4.ngram_accuracy(iaa3_4.ao1.annotated_indices_groups, iaa3_4.ao2.annotated_indices_groups))
    print(iaa3_4.ngram_accuracy(iaa3_4.ao2.annotated_indices_groups, iaa3_4.ao1.annotated_indices_groups))

    ao5 = Annotation(data5)
    iaa1_5 = InterAnnotatorAgreement(ao1, ao5)
    print("1 und 5:", iaa1_5.ngram_mean_accuracy())

    # print("levenshtein 1 und 2:", iaa.levenshtein(ao1.annotated_indices_groups, ao2.annotated_indices_groups))
    # print(InterAnnotatorAgreement.transform_groups_cost([1, 2, 3, 4, 5], [[1, 2], [4, 5]]))
    groups1 = [[0], [3], [9], [13], [16], [19], [20], [23], [24, 25]]
    groups2 = [[0], [3], [9], [13], [16], [19, 20], [23], [24, 25, 26], [27]]
    print(iaa.levenshtein(groups1, groups2))  # should cost 2
    print(iaa.levenshtein(groups2, groups1))
