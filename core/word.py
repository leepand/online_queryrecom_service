__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import jellyfish
def resub_string(string,resub_list=None):
    if resub_list:
        for str_sub in resub_list:
            pat=safe_unicode(str_sub)
            string=re.sub(pat, '', safe_unicode(string))
            return string
    else:
        return safe_unicode(string)
def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text
    else:
        return text.decode('utf-8') 

def edit_distance(x, y, resub_del_list=None):
    """Calculate the hamming distance (number of bits different) between the
    two integers given.
    >>> [hamming_distance(x, 15) for x in [0, 8, 10, 12, 14, 15]]
    [4, 3, 2, 2, 1, 0]
    """
    y=resub_string(safe_unicode(y),resub_del_list)
    x=resub_string(safe_unicode(x),resub_del_list)
    return 1-jellyfish.jaro_winkler(x, y)#bin(x ^ y).count('1')

class Word(object):
    @staticmethod
    def deletes(word, edit_distance):
        """ Recursively create all the possible deletes at a distance * less than or equal to * `edit_distance`
        from the `word` provided. For example, all the possible delete edits of the word `ciao`, at an
        edit distance less than or equal to two are:
        -> cia, cao, cio, iao (distance 1)
        -> ci, ia, ca, ca, ao, co, ci, io, co, ia, ao, io (distance 2)

        Duplicates are suppressed.
        """
        dels = set()
        if len(word) <= 1 or edit_distance == 0:
            return dels
        for i in range(len(word)):
            delete = word[:i] + word[i+1:]  # remove the i-th character from the word
            dels.update([delete])
            dels.update(Word.deletes(delete, edit_distance - 1))
        return dels

    @staticmethod
    def shorter_words_within_distance(word, bag, distance):
        res = set()
        for shorter in Word.deletes(word, distance):
            if not shorter in bag:  # no match
                continue
            bag.remove(shorter)  # no need to visit `shorter` again
            res.update([shorter])
            res.update(Word.shorter_words_within_distance(shorter, bag, distance))
        return res

    @staticmethod
    def damerau_levenshtein_distance(word1, word2):
        return edit_distance(word1, word2)
        """
        A genetic algorithm to compute the Damerau-Levenshtein distance between two words
        
        d = {}
        lenstr1 = len(word1)
        lenstr2 = len(word2)
        for i in xrange(-1, lenstr1 + 1):
            d[(i, -1)] = i + 1
        for j in xrange(-1, lenstr2 + 1):
            d[(-1, j)] = j + 1

        for i in xrange(lenstr1):
            for j in xrange(lenstr2):
                if word1[i] == word2[j]:
                    cost = 0
                else:
                    cost = 1
                d[(i, j)] = min(
                    d[(i - 1, j)] + 1,  # deletion
                    d[(i, j - 1)] + 1,  # insertion
                    d[(i - 1, j - 1)] + cost,  # substitution
                )
                if i and j and word1[i] == word2[j - 1] and word1[i - 1] == word2[j]:
                    d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition

        return d[lenstr1 - 1, lenstr2 - 1]
        """

