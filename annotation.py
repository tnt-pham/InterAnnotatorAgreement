# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 09-Jun-2021
# Python 3.7
# Windows 10
"""Preprocessing of an annotated text."""


class Annotation:
    """Transforms annotated text to Annotation object.
    Examples of possible text annotations:
        example1 = '[Ali] has [a small dog].'
        example2 = '<Ali> has a small <dog>.'

    Args:
        text (str): Text that is annotated.
        opening_bracket (str): Marks start of annotated element.
            Defaults to '['.
        closing_bracket (str): Marks end of annotated element.
            Defaults to ']'.

    Attributes:
        text_split (list): Split text by whitespace character.
        opening_bracket (str): Opening bracket.
        closing_bracket (str): Closing bracket.
        annotated_indices (set): Contains those indices that are
            annotated.
        annotated_indices_groups (list): Contains lists of indices that
            are annotated as one markable.
        not_annotated_indices_groups (list): Consists of lists so that
            each contains one index that is not annotated as a markable.

    Raises:
        ValueError: If given text is empty.
    """
    def __init__(self, text, opening_bracket='[', closing_bracket=']'):
        if not text:
            raise ValueError("Text cannot be empty.")

        self.text_split = text.split()
        self.opening_bracket = opening_bracket
        self.closing_bracket = closing_bracket
        self.annotated_indices = set()
        self.annotated_indices_groups = []
        self.not_annotated_indices_groups = []

        self._extract_indices()

    def _extract_indices(self):
        """Gets and groups indices of annotated/not annotated words."""
        in_brackets = False
        for num, word in enumerate(self.text_split):
            if word.startswith(self.opening_bracket):
                in_brackets = True
                group = []
            if in_brackets:  # annotated as markable
                self.annotated_indices.add(num)
                group.append(num)
            if word.rstrip(",.;:-?!'\")").endswith(self.closing_bracket):
                in_brackets = False
                self.annotated_indices_groups.append(group)
            elif not in_brackets:  # not annotated as markable
                self.not_annotated_indices_groups.append([num])


if __name__ == "__main__":
    text = ("[Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass"
            " [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie]"
            " verließ augenblicklich [den großen Raum], als [Peter]"
            " [seinen Mund] öffnete.")
    ao = Annotation(text)

    print("####### Welcome to the Demo #######")
    print("Let's create an Annotation object!")
    print(f">>> text = '{text}'")
    print(">>> ao = Annotation(text)")
    print("")
    print(">>> print(ao.annotated_indices)")
    print(ao.annotated_indices)
    print(">>> print(ao.annotated_indices_groups)")
    print(ao.annotated_indices_groups)
