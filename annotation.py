# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 03-Jun-2021
# Python 3.7
# Windows 10
"""Transforms annotated text to Annotation object."""


class Annotation:
    """Transforms annotated text to Annotation object."""
    def __init__(self, text, opening_bracket='[', closing_bracket=']'):
        self.text_split = text.split()
        self.opening_bracket = opening_bracket
        self.closing_bracket = closing_bracket
        self.annotated_indices = set()
        self.annotated_indices_groups = []
        self.not_annotated_indices_groups = []

        self.extract_indices()

    def extract_indices(self):
        """Get indices of annotated words."""
        in_brackets = False
        for num, word in enumerate(self.text_split):
            if word.startswith(self.opening_bracket):
                in_brackets = True
                group = []
            if in_brackets:
                self.annotated_indices.add(num)
                group.append(num)
            if word.rstrip(",.;:-").endswith(self.closing_bracket):  # TODO: before comma or full stop
                in_brackets = False
                self.annotated_indices_groups.append(group)
            elif not in_brackets:
                self.not_annotated_indices_groups.append([num])


if __name__ == "__main__":
    text = "[Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete."
    ao = Annotation(text)
    print(len(ao.text_split))
    print(ao.annotated_indices)
    print(ao.annotated_indices_groups)
    print(ao.not_annotated_indices_groups)
