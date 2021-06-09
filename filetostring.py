# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 09-Jun-2021
# Python 3.7
# Windows 10
"""Supplementary class for file reading."""


class FileToString:
    """Retrieves text from a file.

    Args:
        file (str): Path of the file.
        encoding (str): File encoding. Defaults to 'utf-8'.

    Attributes:
        text (str): Text read from the file.

    Raises:
        FileNotFoundError: If given file path does not exist.
        PermissionError: If given file path leads to a directory.
    """
    def __init__(self, file, encoding="utf-8"):
        self.text = self._file_to_string(file, encoding=encoding)

    def _file_to_string(self, file, encoding="utf-8"):
        """Retrieves text from a file."""
        try:
            with open(file, 'r', encoding=encoding) as read_f:
                text = read_f.read()
        except FileNotFoundError as fnf:
            fnf_msg = file + " does not exist."
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except PermissionError as pe:
            pe_msg = file + " does not lead to a file."
            raise PermissionError(pe_msg).with_traceback(pe.__traceback__)
        return text
