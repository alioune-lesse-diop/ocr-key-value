import pytesseract
from PIL import Image
from itertools import groupby
import numpy as np
from spacy.lang.en import English

nlp = English()

# schema = [u'level', u'page_num', u'block_num', u'par_num', u'line_num', u'word_num', u'left', u'top', u'width', u'height', u'conf', u'text']

LINE_INDEX = 4
CONF_INDEX = -2
WORD_INDEX = -1
LEFT_INDEX = -6
WIDTH_INDEX = -4

def processingOneLineOfWords(words, joinThreshold = 10):
    wordDistanceArr = map(lambda p: p[1][LEFT_INDEX] - (p[0][LEFT_INDEX] + p[0][WIDTH_INDEX]), zip(words, words[1:]))
    shouldSplitBecauseOfText = np.array(map(lambda w: w[WORD_INDEX][0] == '|', words[1:]))
    shouldSplitBecauseOfDistance = np.array(wordDistanceArr) > joinThreshold
    shouldSplit = list((shouldSplitBecauseOfText + shouldSplitBecauseOfDistance)>0 +0)
    phraseIds = reduce(lambda s,x: s + [x+s[-1]] , shouldSplit, [0])
    # print(phraseIds)
    wordGroups = [map(lambda p: p[0], it) for k, it in groupby(zip(words, phraseIds), lambda p: p[1])]

    return map(lambda arr: arr[0][0:WORD_INDEX] + [' '.join(map(lambda w: w[WORD_INDEX], arr))], wordGroups)

def extract_data(img_file_path):
    data = pytesseract.image_to_data(Image.open(img_file_path))
    # print(data)
    arrays = map(lambda s: s.split('\t'), data.split('\n'))[1:]
    words = map(lambda arr: arr[0:6] + map(lambda i: int(i), arr[6:-1]) + [arr[-1]], arrays)
    words = filter(lambda arr: arr[CONF_INDEX] >0 and arr[WORD_INDEX], words)
    lines = [processingOneLineOfWords(map(lambda x: x, it)) for k, it in groupby(words, lambda arr: ','.join(arr[0:5]))]
    return [lines]

def extract_key_values_from_line(line):
    hasNumbers = map(lambda phrase: reduce(lambda s,t: s+t.like_num, nlp(phrase[WORD_INDEX]), 0), line)
    return filter(lambda v: v, [[line[i-1][WORD_INDEX], line[i][WORD_INDEX]] if v > 0 and not hasNumbers[i-1] else None for i, v in enumerate(hasNumbers)])

#[lines] = extract_data('/tmp/1.png')
#[lines] = extract_data('/tmp/R85K-EwL-L5FOBhgHJuTyw.png')
[lines] = extract_data('/tmp/E6Wty2FyTTLXg55IR5jOlQ.png')

pairs = filter(lambda l: len(l)>0, map(extract_key_values_from_line, lines))
for p in pairs:
    print(p)
