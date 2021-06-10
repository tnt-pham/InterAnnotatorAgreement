# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 09-Jun-2021
# Python 3.7
# Windows 10
"""Tool to ascertain similarity between two Annotation objects."""

import os

from annotation import Annotation
from errors import DifferentTextException
from filetostring import FileToString


class InterAnnotatorAgreement:
    """Provides metrics to ascertain the InterAnnotatorAgreement (IAA)
    between two different text annotations.

    Args:
        annotation_obj1 (Annotation): One of the text annotations.
        annotation_obj2 (Annotation): One of the text annotations.

    Attributes:
        ao1 (Annotation): One of the text annotations.
        ao2 (Annotation): One of the text annotations.

    Raises:
        DifferentTextException: If the two annotated texts are different
            or if annotation guideline violations are encountered.
    """
    def __init__(self, annotation_obj1, annotation_obj2):
        if len(annotation_obj1.text_split) != len(annotation_obj2.text_split):
            raise DifferentTextException("Two Annotation objects are"
                                         " incompatible. Please check"
                                         " the annotation guidelines.")

        self.ao1 = annotation_obj1
        self.ao2 = annotation_obj2

    def _naive_count_agreement(self):
        """Counts how many tokens (orthographic words) are annotated/
        not annotated in both annotations equally, regardless of the
        boundaries (= in brackets or not), and how many tokens are
        annotated differently.

        Returns:
            tuple: 3-tuple consisting of:
                number of tokens that are in brackets in both
                    annotations (int),
                number of tokens that are not in brackets in both
                    annotations (int),
                number of disagreements (int)
        """
        same_in_bracket = len(
            self.ao1.annotated_indices.intersection(self.ao2.annotated_indices)
            )
        disagree = len(
            self.ao1.annotated_indices.symmetric_difference(
                self.ao2.annotated_indices)
            )
        same_not_bracket = (len(self.ao1.text_split)
                            - same_in_bracket
                            - disagree)
        return same_in_bracket, same_not_bracket, disagree

    def naive_accuracy(self):
        """Calculates the proportion of agreeing annotations.

        Returns:
            float: Proportion of agreeing annotations. Between 0 and 1.
        """
        (same_in_bracket,
         same_not_bracket,
         disagree) = self._naive_count_agreement()
        return ((same_in_bracket + same_not_bracket)
                / (same_in_bracket + same_not_bracket + disagree))

    def _ngreement(self, indice_groups_ref, indice_groups_comp, n=2):
        """NGram-based agreement.
        Ascertains how well an annotation is compatible with
        a reference. Takes subset relations into account.
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
            n (int): Increasing n increases the reward for correctly
                annotated long markables. Defaults to 2.

        Returns:
            float: Ratio of achieved score and maximum possible score
                (see example above). Between 0 and 1.
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
        """Calculates the mean ngreement by treating each annotation
        once as a reference.

        Args:
            n (int): Increasing n increases the reward for correctly
                annotated long markables. Defaults to 2.

        Returns:
            float: Mean NGreement. Between 0 and 1.
        """
        annotated_acc1 = self._ngreement(self.ao1.annotated_indices_groups,
                                         self.ao2.annotated_indices_groups,
                                         n=n)
        not_annotated_acc1 = self._ngreement(self.ao1.not_annotated_indices_groups,
                                             self.ao2.not_annotated_indices_groups,
                                             n=n)
        annotated_acc2 = self._ngreement(self.ao2.annotated_indices_groups,
                                         self.ao1.annotated_indices_groups,
                                         n=n)
        not_annotated_acc2 = self._ngreement(self.ao2.not_annotated_indices_groups,
                                             self.ao1.not_annotated_indices_groups,
                                             n=n)
        # no markables are annotated at all
        if (len(self.ao1.annotated_indices_groups) == 0
            and len(self.ao2.annotated_indices_groups) == 0):
            return 1.0
        return (annotated_acc1 + annotated_acc2
                + not_annotated_acc1 + not_annotated_acc2)/4

    @staticmethod
    def get_subgrams(ngram):
        """Creates power set (as list) of the ngram (= subgrams)
            without empty list.
        Example:
            ngram = [4, 5, 6]
            subgrams = [[4, 5, 6], [5, 6], [6], [4, 5], [5], [4]]

        Args:
            ngram (list): Represents ngram,
                i.e. contains the corresponding indices (int).

        Returns:
            list: Contains subgrams (= lists of indices (int)).
                First list is equivalent to full ngram.
        """
        subgrams = []
        # shortens list from the right hand side
        for i in range(len(ngram), 0, -1):
            # shortens list from the left hand side
            for j in range(i):
                subgrams.append(ngram[j:i])
        return subgrams

    def _levenshtein(self, indices_groups_ref, indices_groups_comp):
        """Computes levenshtein distance, the number of
        editing operations until both lists are equal.
        Example:
            indices_groups_ref = [[0, 1], [3], [5, 6, 7]]
            indices_groups_comp = [[0], [5, 6, 7, 8]]
            distance =
            Note: The distance is symmetric. Therefore the result
            is not affected by the choice of the reference annotation.

        Args:
            indices_groups_ref (list): Contains grouped indices
                (one sublist for each markable).
            indices_groups_comp (list): Contains grouped indices
                (one sublist for each markable).

        Returns:
            int: Levenshtein distance >= 0.
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
            return self._levenshtein(indices_groups_ref[1:],
                                     indices_groups_comp[1:])
        else:
            if self.is_compatible(indices_groups_ref[0],
                                  indices_groups_comp[0]):
                # until this index, groups in comp can be transformed to ref
                compatible_index_boundary_in_ref = (
                    self._find_compatible_index_boundary(
                        indices_groups_comp[0], indices_groups_ref)
                    )
                compatible_index_boundary_in_comp = (
                    self._find_compatible_index_boundary(
                        indices_groups_ref[0], indices_groups_comp)
                    )

                if (compatible_index_boundary_in_ref
                    < compatible_index_boundary_in_comp):
                    return (self._transform_groups_cost(
                        indices_groups_ref[0],
                        indices_groups_comp[:compatible_index_boundary_in_comp]
                        )
                            + self._levenshtein(
                                indices_groups_ref[1:],
                                indices_groups_comp[compatible_index_boundary_in_comp:])
                                )
                else:
                    return (self._transform_groups_cost(
                        indices_groups_comp[0],
                        indices_groups_ref[:compatible_index_boundary_in_ref]
                        )
                            + self._levenshtein(
                                indices_groups_ref[compatible_index_boundary_in_ref:],
                                indices_groups_comp[1:])
                                )

            else:  # first groups disagree completely
                # first ref group is missing
                if indices_groups_ref[0][0] < indices_groups_comp[0][0]:
                    return 1 + self._levenshtein(indices_groups_ref[1:],
                                                 indices_groups_comp)
                else:  # first comp group is too much
                    return 1 + self._levenshtein(indices_groups_ref,
                                                 indices_groups_comp[1:])

    def levenshtein_incl_normalized(self):
        """Normalizes levenshtein distance
        by mean number of identified markables.

        Returns:
            tuple: 2-tuple consisting of absolute distance (int)
                and normalization (float).
        """
        distance = self._levenshtein(self.ao1.annotated_indices_groups,
                                     self.ao2.annotated_indices_groups)
        markable_count1 = len(self.ao1.annotated_indices_groups)
        markable_count2 = len(self.ao2.annotated_indices_groups)
        return distance, distance/max(markable_count1, markable_count2)

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

    @staticmethod
    def _find_compatible_index_boundary(group_ref, indices_groups_comp):
        """Finds the maximum number of groups (in indices_groups_comp)
        whose members (indices) are part of the reference.
        This number is equivalent to the starting index (if existent)
        from where on no more matches are possible.
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


if __name__ == "__main__":
    text1 = ("[Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass"
             " [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie]"
             " verließ augenblicklich [den großen Raum], als [Peter]"
             " [seinen Mund] öffnete.")
    text2 = ("[Er] geht zu Lisa. [Niemand] hat damit gerechnet, dass"
             " [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie]"
             " verließ augenblicklich [den großen Raum], als [Peter]"
             " [seinen Mund] öffnete.")
    ao1 = Annotation(text1)
    ao2 = Annotation(text2)
    iaa = InterAnnotatorAgreement(ao1, ao2)
    dir_name = "testdata"
    file_path1 = os.path.join(dir_name, "text1.txt")
    file_path2 = os.path.join(dir_name, "text2.txt")
    fts1 = FileToString(file_path1)
    fts2 = FileToString(file_path2)

    print("####### Welcome to the demo #######")
    print("How to ascertain the similarity of two annotated texts:")
    print("")
    print(f">>> text1 = '{text1}'")
    print(f">>> text2 = '{text2}'")
    print("But what if the texts are saved as files? No problem!")
    print(f">>> fts1 = FileToString('{file_path1}')")
    print(f">>> fts2 = FileToString('{file_path2}')")
    print(">>> text1 = fts1.text")
    print(">>> text2 = fts2.text")
    print("")
    print("Let us create an Annotation object of each text!")
    print(">>> ao1 = Annotation(text1)")
    print(">>> ao2 = Annotation(text2)")
    print("")
    print("Now create an InterAnnotatorAgreement object!")
    print(">>> iaa = InterAnnotatorAgreement(ao1, ao2)")
    print("")
    print(">>> print(iaa.naive_accuracy())")
    print(iaa.naive_accuracy())
    print(">>> print(iaa.mean_ngreement())")
    print(iaa.mean_ngreement())
    print(">>> print(iaa.levenshtein_incl_normalized())")
    print(iaa.levenshtein_incl_normalized())
