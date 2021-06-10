This project was written on Windows 10, Python 3.7.3.  
Visit me on [GitHub](https://github.com/thommy24/InterAnnotatorAgreement) for latest updates and infos!

## NAME
main.py - command line tool for calculating similarity metrics for two text annotations.

## DESCRIPTION
Annotating linguistic data can be an onerous task. Some try to automatically annotate text, but this is quite difficult sometimes. Depending on the task we see even humans disagree with each other a lot. Coreference resolution is a field of research which still needs some attention and to fulfil this task one must identify the so-called markables beforehand. These are the segments which possibly can be referred to or refer to other segments. Having two people annotating markables in a text, we wonder how similar their annotations are. This program provides three useful metrics to assess the similarity between these two annotations, also called the InterAnnotatorAgreement (IAA).

### ANNOTATION GUIDELINES
**Format:**  
The brackets that are used to annotate the markables should be set around the markables, without inserting any whitespaces. The following examples are possible annotations:  
A1: [Sie] verließ augenblicklich [den großen Raum], als [Peter] [seinen Mund] öffnete.  
A2: Sie verließ augenblicklich [den] [großen] [Raum], als [Peter] [seinen Mund] öffnete.  

### METRICS
**Naive:** The proportion of agreeing in-brackets as well as not-in-brackets and total number of tokens. = 10/11  
    - Calculation: number_of_agreeing_annotations/ total_number_of_tokens = 10/11  
    - Value Range: from 0 (not similar) to 1 (most similar)  
    - Limitation: Does not take into account the markable boundaries. `[den großen Raum]` and `[den] [großen] [Raum]` are treated the same.  
**NGram:** How well an annotation is compatible with a reference. Takes subset relations into account. The longer the agreeing markables, the higher the reward.  
    - Calculation: Consider one annotation as the reference. Now compute: max_score = sum of the squares of the lengths of all reference markables. Then compute: score = sum of all the squares of the lengths of the other annotation's markables IF the markable is also in the reference  or the markable is contained in a larger reference markable. Calculate the ratio of score/max_score. Repeat the calculation with the reversed perspective, i.e. the 'other' annotation is the reference now and vice versa. Then repeat these two calculations, but this time each of the not-annotated tokens is a markable and the before-annotated markables are not-annotated tokens now. Average these 4 results and get the ngram-agreement, also called 'ngreement'.  
    - Value Range: from 0 (not similar) to 1 (same)  
    - Limitation: Agreeing long markables can result in a high value although a lot of other short markables are annotated differently.
**Levenshtein:** Distance: The number of editing operations until the two annotations are the same. Normalized: Number of editing operations per markable.  
    - Calculation: Distance: Deleting/adding a pair of brackets (= 1), merge two markables (= 1). Normalized: distance/max(number of markables of one annotation, number of markables of other annotation)  
    - Value Range: Distance: from 0 (same) to infinity (not similar); Normalized: from 0 (same) to 2 (not similar)
    - Limitation: from `als [Peter] [seinen Mund]` to `als [Peter seinen] Mund` 2 edits (delete(Mund) + merge(Peter, seinen))  
    but from `als [Peter] [seinen Mund]` to `als [Peter seinen] [Mund]` 3 edits (merge(Peter, seinen Mund) + delete(Mund) + add(Mund)) although intuitively more similar.
    - Side note: Implementation can be improved and adjusted to this problem. Add 'demerge' operation (= 1) and substitute 'delete+add' (= 2).

##  REQUIREMENTS
- two annotations of the **same text** (as strings or in files)

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