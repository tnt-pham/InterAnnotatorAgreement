# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 03-Jun-2021
# Python 3.7
# Windows 10
"""Reads text from a file."""
# logger name? same as iaa?

class FileToString:  # or rather FileToString?
    def __init__(self, file, encoding="utf-8"):
        self.text = self.file_to_string(file, encoding=encoding)

    def file_to_string(self, file, encoding="utf-8"):
        try:
            with open(file, 'r', encoding=encoding) as read_f:
                text = read_f.read()
        except FileNotFoundError as fnf:
            fnf_msg = file +" does not exist."
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except PermissionError as pe:
            pe_msg = file + " does not lead to a file."
            raise FileNotFoundError(pe_msg).with_traceback(pe.__traceback__)
        return text


if __name__ == "__main__":
    fr = FileToString("testdata\\text1.txt")
    print(fr.text)
    print(len(fr.text.split()))
