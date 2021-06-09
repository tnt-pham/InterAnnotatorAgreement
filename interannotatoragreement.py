# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 03-Jun-2021
# Python 3.7
# Windows 10
"""Ascertains similarity between two Annotation objects."""

import re

from annotation import Annotation
from errors import DifferentTextException


class InterAnnotatorAgreement:
    """Provides metrics to ascertain the InterAnnotatorAgreement (IAA) between different text annotations.
    Possible text annotations can be:
    annotated_text1 = '[Ali] has [a small dog].'
    annotated_text2 = '[Ali] has a small [dog].'

    Args:
        annotation_obj1 (Annotation): ...
        annotation_obj1 (Annotation): ...

    Attributes:
        ao1 (Annotation): ...
        ao1 (Annotation): ...

    Raises:
        DifferentTextException: If the two annotated texts are different or if annotation guideline violations are encountered.
    """
    def __init__(self, annotation_obj1, annotation_obj2):
        if len(annotation_obj1.text_split) != len(annotation_obj2.text_split):
            raise DifferentTextException("Two Annotation objects are incompatible. Please check the annotation guidelines.")  # how to set brackets

        self.ao1 = annotation_obj1
        self.ao2 = annotation_obj2

    def naive_count_agreement(self):
        """Counts how many tokens (orthographic words) are annotated/not annotated in both annotations equally, regardless the boundaries (= in brackets or not), and how many tokens are annotated differently.

        Returns:
            tuple: 3-tuple consisting of number of tokens that are in brackets in both annotations (int),
                number of tokens that are not in brackets in both annotations (int),
                number of disagreements (int)
        """
        same_in_bracket_count = len(self.ao1.annotated_indices.intersection(self.ao2.annotated_indices))
        disagree_count = len(self.ao1.annotated_indices.symmetric_difference(self.ao2.annotated_indices))
        same_not_bracket_count = len(self.ao1.text_split) - same_in_bracket_count - disagree_count
        return same_in_bracket_count, same_not_bracket_count, disagree_count

    def naive_accuracy(self):
        """Calculates the proportion of agreeing annotations.

        Returns:
            float: Proportion of agreeing annotations. Between 0 and 1.
        """
        same_in_bracket_count, same_not_bracket_count, disagree_count = self.naive_count_agreement()
        return (same_in_bracket_count + same_not_bracket_count)/(same_in_bracket_count + same_not_bracket_count + disagree_count)

    def ngreement(self, indice_groups_ref, indice_groups_comp, n=2):
        """NGram-based agreement. Ascertains how well an annotation is compatible with a reference. Takes subset relations into account.
        Example:
            indice_groups_ref = [[0], [2, 3, 4]]
            indice_groups_comp = [[0], [3, 4]]
            max_score = 1**2 + 3**2 = 10
            score = 1**2 + 2**2 = 5
            ngreement = 5/10 = 0.5
            Note: We call [3, 4] a subgram of [2, 3, 4].

        Args:
            indice_groups_ref (list): Contains lists of indices (int).
            indice_groups_comp (list): Contains lists of indices (int).
            n (int): Increasing n increases the reward for correctly annotated long markables. Defaults to 2.

        Returns:
            float: Ratio of achieved score and maximum possible score (see example above).
        """
        max_score = 0
        score = 0
        subgrams = []  # to be filled with lists of lists of indices
        for group in indice_groups_ref:
            subgrams.append(self.get_subgrams(group))
            max_score += len(group)**n
        for group in indice_groups_comp:
            # first elem is always the largest group with every index
            for subgram in subgrams:
                # compare both smallest indices
                if group[0] < subgram[0][0]:
                    break  # because indices in subgrams only get higher
                if group[0] not in subgram[0]:
                    continue
                if group in subgram:
                    score += len(group)**n
                    break
        if max_score == 0:
            return 0.0
        return score/max_score

    def mean_ngreement(self, n=2):
        """Calculates the mean ngreement by treating each annotation once as a reference.

        Args:
            n (int): Increasing n increases the reward for correctly annotated long markables. Defaults to 2.

        Returns:
            float: Mean NGreement.
        """
        annotated_acc1 = self.ngreement(self.ao1.annotated_indices_groups, self.ao2.annotated_indices_groups, n=n)
        not_annotated_acc1 = self.ngreement(self.ao1.not_annotated_indices_groups, self.ao2.not_annotated_indices_groups, n=n)
        annotated_acc2 = self.ngreement(self.ao2.annotated_indices_groups, self.ao1.annotated_indices_groups, n=n)
        not_annotated_acc2 = self.ngreement(self.ao2.not_annotated_indices_groups, self.ao1.not_annotated_indices_groups, n=n)
        return (annotated_acc1 + annotated_acc2 + not_annotated_acc1 + not_annotated_acc2)/4

    @staticmethod
    def get_subgrams(ngram_indices):
        """Creates power set (as list) of ngram (= subgrams) without empty list.
        Example:
            ngram_indices = [4, 5, 6]
            subgrams = [[4, 5, 6], [5, 6], [6], [4, 5], [5], [4]]

        Args:
            ngram_indices (list): Represents ngram, i.e. contains the corresponding indices (int).

        Returns:
            list: Contains subgrams (= lists of indices (int)). First list is equivalent to full ngram.
        """
        subgrams = []
        # shortens list from the right hand side
        for i in range(len(ngram_indices), 0, -1):
            # shortens list from the left hand side
            for j in range(i):
                subgrams.append(ngram_indices[j:i])
        return subgrams

    def levenshtein(self, indices_groups_ref, indices_groups_comp):
        """Computes levenshtein distance, the number of editing operations until both lists are equal.
        Example:
            indices_groups_ref = [[0, 1], [3], [5, 6, 7]]
            indices_groups_comp = [[0], [5, 6, 7, 8]]
            distance =
            Note: The distance is symmetric. Therefore the result is not affected by the choice of the reference annotation.

        Args:
            indices_groups_ref (list): Contains grouped indices (one sublist for each markable).
            indices_groups_comp (list): Contains grouped indices (one sublist for each markable).

        Returns:
            int: Levenshtein distance.
        """
        # base cases
        if len(indices_groups_ref) == 0 and len(indices_groups_comp) == 0:
            return 0
        if len(indices_groups_ref) == 0:
            return len(indices_groups_comp)  # number of superfluous groups
        if len(indices_groups_comp) == 0:
            return len(indices_groups_ref)  # number of missing groups

        # recursive cases
        if indices_groups_ref[0] == indices_groups_comp[0]:
            return self.levenshtein(indices_groups_ref[1:], indices_groups_comp[1:])
        else:
            if self.is_compatible(indices_groups_ref[0], indices_groups_comp[0]):
                # until this index, groups in comp can be transformed to ref
                compatible_index_boundary_in_ref = self._find_compatible_index_boundary(indices_groups_comp[0], indices_groups_ref)
                compatible_index_boundary_in_comp = self._find_compatible_index_boundary(indices_groups_ref[0], indices_groups_comp)

                if compatible_index_boundary_in_ref < compatible_index_boundary_in_comp:
                    return self._transform_groups_cost(indices_groups_ref[0], indices_groups_comp[:compatible_index_boundary_in_comp]) + self.levenshtein(indices_groups_ref[1:], indices_groups_comp[compatible_index_boundary_in_comp:])
                else:
                    return self._transform_groups_cost(indices_groups_comp[0], indices_groups_ref[:compatible_index_boundary_in_ref]) + self.levenshtein(indices_groups_ref[compatible_index_boundary_in_ref:], indices_groups_comp[1:])

            else:  # first groups disagree completely
                # first ref group is missing
                if indices_groups_ref[0][0] < indices_groups_comp[0][0]:
                    return 1 + self.levenshtein(indices_groups_ref[1:], indices_groups_comp)
                else:  # first comp group is too much
                    return 1 + self.levenshtein(indices_groups_ref, indices_groups_comp[1:])

    def levenshtein_incl_normalized(self):
        """Normalizes levenshtein distance by mean number of identified markables.

        Returns:
            tuple: 2-tuple consisting of absolute distance (int) and normalization (float).
        """
        distance = self.levenshtein(self.ao1.annotated_indices_groups, self.ao2.annotated_indices_groups)
        markable_count1 = len(self.ao1.annotated_indices_groups)
        markable_count2 = len(self.ao2.annotated_indices_groups)
        return distance, distance/((markable_count1 + markable_count2)/2)

    @staticmethod
    def _transform_groups_cost(group_ref, indices_groups_comp):
        """Ascertains number of required editing operations."""
        set_ref = set(group_ref)
        set_comp = set()
        for group in indices_groups_comp:
            set_comp.update(set(group))
        add_delete_cost = len(set_ref.symmetric_difference(set_comp))
        merge_cost = len(indices_groups_comp) - 1
        return add_delete_cost + merge_cost

    @staticmethod
    def is_compatible(group_ref, group_comp):
        """Checks whether the two groups share at least one index.

        Args:
            group_ref (list): Contains indices of one group (= ngram).
            group_comp (list): Contains indices of one group (= ngram).

        Return:
            bool: True if shared index exists, else False.
        """
        for index in group_comp:
            if index in group_ref:
                return True
        return False

    # @staticmethod
    # def find_index(searchlist, element):
    #     """Get """
    #     for num, list_el in enumerate(searchlist):
    #         if list_el == element:
    #             return num
    #     return -1

    @staticmethod
    def _find_compatible_index_boundary(group_ref, indices_groups_comp):
        """Finds the maximum number of groups (in indices_groups_comp) whose members (indices) are part of the reference.
        This number is equivalent to the starting index (if existent) from where on no more matches are possible.
        Example:
        group_ref = [6, 7, 8]
        indices_groups_comp = [[6], [7, 8, 9], [10], [11]]
        index_boundary = 2
        """
        for num1, group in enumerate(indices_groups_comp):
            for num2, index in enumerate(group):
                if index not in group_ref:
                    if num2 == 0:  # whole group already incompatible
                        return num1
                    return num1 + 1  # part of the group compatible
        return num1 + 1


# def find_context(text):
#     pattern = r"\w*\s*\[.+?\]\s*\w*"
#     return re.findall(pattern, text)


# def find_markables(text):
#     pattern = r"\[.+?\]"
#     return re.findall(pattern, text)


if __name__ == "__main__":
    data1 = "[Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    data2 = "[Er] geht zu Lisa. [Niemand] hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    data3 = "[Er geht zu Lisa]. [Niemand hat damit gerechnet, dass Laura dabei sein würde]. [Fatma ist entsetzt]. [Sie verließ augenblicklich den großen Raum], [als Peter seinen Mund öffnete]."
    data4 = "[Er] [geht] [zu] [Lisa]. [Niemand] [hat] [damit] [gerechnet], [dass] [Laura] [dabei] [sein] [würde]. [Fatma] [ist] [entsetzt]. [Sie] [verließ] [augenblicklich] [den] [großen] [Raum], [als] [Peter] [seinen] [Mund] [öffnete]."
    data5 = "[Er] geht zu Lisa. [Niemand hat] damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    data6 = "Er geht zu Lisa. Niemand hat damit gerechnet, dass Laura dabei sein würde. Fatma ist entsetzt. Sie verließ augenblicklich den großen Raum, als Peter seinen Mund öffnete."

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

    print("1 und 2:", iaa.mean_ngreement())

    ao3 = Annotation(data3)
    iaa1_3 = InterAnnotatorAgreement(ao1, ao3)
    print("1 und 3:", iaa1_3.mean_ngreement())

    iaa1_1 = InterAnnotatorAgreement(ao1, ao1)
    print("1 und 1:", iaa1_1.mean_ngreement())

    ao4 = Annotation(data4)
    iaa3_4 = InterAnnotatorAgreement(ao3, ao4)
    print("3 und 4:", iaa3_4.mean_ngreement())
    print(iaa3_4.ngreement(iaa3_4.ao1.annotated_indices_groups, iaa3_4.ao2.annotated_indices_groups))
    print(iaa3_4.ngreement(iaa3_4.ao2.annotated_indices_groups, iaa3_4.ao1.annotated_indices_groups))

    ao5 = Annotation(data5)
    iaa1_5 = InterAnnotatorAgreement(ao1, ao5)
    print("1 und 5:", iaa1_5.mean_ngreement())

    # print("levenshtein 1 und 2:", iaa.levenshtein(ao1.annotated_indices_groups, ao2.annotated_indices_groups))
    # print(InterAnnotatorAgreement._transform_groups_cost([1, 2, 3, 4, 5], [[1, 2], [4, 5]]))
    groups1 = [[0], [3], [9], [13], [16], [19], [20], [23], [24, 25]]
    groups2 = [[0], [3], [9], [13], [16], [19], [20], [23], [25]]
    print(iaa.levenshtein(groups1, groups2))  # should cost 1
    print(iaa.levenshtein(groups2, groups1))
    print(iaa.levenshtein_incl_normalized())
