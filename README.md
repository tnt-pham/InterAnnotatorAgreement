This project was written on Windows 10, Python 3.7.3.  
Visit me on [GitHub](https://github.com/thommy24/InterAnnotatorAgreement) for latest updates and infos!

## NAME
main.py - command line tool for calculating similarity metrics for two text annotations.

## DESCRIPTION
Annotating linguistic data can be an onerous task. Some try to automatically annotate text, but this is quite difficult sometimes. Depending on the task we see even humans disagree with each other a lot. Coreference resolution is a field of research which still needs some attention and to fulfil this task one must identify the so-called markables beforehand. These are the segments which possibly can be referred to or refer to other segments. Having two people annotating markables in a text, we wonder how similar their annotations are. This program provides three useful metrics to assess the similarity between these two annotations, also called the InterAnnotatorAgreement (IAA).

### ANNOTATION GUIDELINES
**Format:**  
Possible annotation 1: [Er] geht zu [Lisa]. Niemand hat damit gerechnet, dass [Laura] dabei sein würde. [Fatma] ist entsetzt. [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete.

only 2 same texts

##  REQUIREMENTS
- two annotations of the same text (as strings or in files)

## SYNOPSIS
- show command line syntax and more information on arguments
> python main.py --help

- options overview
> python main.py [-h, --help] [-t, --text TEXT TEXT | -f, --file FILE FILE] [--naive] [--ngram] [--levenshtein] [--encoding ENC] [--opening BRACKET] [--closing BRACKET]

- compare two text annotations (as strings) and get the naive and ngram similarity as well as the levenshtein distance
> python main.py --text TEXT TEXT --naive --ngram --levenshtein [--opening BRACKET]? [--closing BRACKET]?

- compare two text annotations from files and get the naive and ngram similarity as well as the levenshtein distance
> python main.py --file FILE FILE --naive [--encoding ENC]? [--opening BRACKET]? [--closing BRACKET]?

- Side notes:
    - You can use either `--text` or `--file` at once.

### ARGUMENTS
- TEXT
    - string (= concatenation of characters)
    - annotated text
- FILE
    - path to/name of a text file
    - contains annotated text
- ENC
    - encoding such as `utf-8`, `utf-16`, `utf-32`, `windows-1250`, `big5`, `latin-1`, `ascii`, ...
    - defaults to `utf-8`
    - specifies both FILE arguments
- BRACKET
    - specifies character(s) that is/are used to annotate markables
    - opening bracket defaults to `[`
    - closing bracket defaults to `]`
- Side note:
    - make sure to enclose the argument with quotation marks `""`

### EXAMPLES
- compare two text annotations (as strings) and get the naive similarity metric  
`python main.py -t "[Ali] hat [zwei Hunde]." "[Ali] hat zwei [Hunde]." --naive`

- compare two text annotations (as strings) and get all similarity metrics  
`python main.py -t "[Ali] hat [zwei Hunde]." "[Ali] hat zwei [Hunde]." --naive --ngram --levenshtein`

- compare two text annotations (as strings) and get all similarity metrics, additionally specify brackets  
`python main.py -t "(Ali) hat (zwei Hunde)." "(Ali) hat zwei (Hunde)." --naive --ngram --levenshtein --opening ( --closing )`

- compare two text annotations from utf-8-encoded files and get the ngram similarity metric  
`python main.py -t "testdata\\text1.txt" "testdata\\text2.txt" --ngram`

- compare two text annotations from latin-1-encoded files and get the ngram similarity metric  
`python main.py -t "testdata\\text1.txt" "testdata\\text2.txt" --ngram --encoding latin-1`

## AUTHOR
Thomas N. T. Pham  
University of Potsdam, June 2021  
[My Github](https://github.com/thommy24/InterAnnotatorAgreement)  
For more information or questions, feel free to contact nhpham@uni-potsdam.de