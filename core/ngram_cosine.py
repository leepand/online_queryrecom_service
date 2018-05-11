from core import ngram
import numpy as np
def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text
    else:
        return text.decode('utf-8') 
def make_terms_from_string(s,gram_filter=False,n=2):
    """turn string s into a list of unicode terms"""
    u = safe_unicode(s)
    #print (ngram.CharNgrams(u,n).d)
    return ngram.CharNgrams(u,gram_filter,n).d#u.split()

def distance_cosine_measure(t1, t2,gram_filter=False,n=2):
    """Calculate cosine similarity of two strings, return as a distance (1==absolutely different, 0==no difference),
       Background: http://en.wikipedia.org/wiki/Cosine_similarity"""
    
    def __cosine_similarity(v1, v2):
        norm_a = np.linalg.norm(v1)  # sqrt of sum of all-items-squared
        norm_b = np.linalg.norm(v2)
        abs_a_abs_b = norm_a * norm_b
        if abs_a_abs_b == 0:
            return 0
        else:
            a_dot_b = np.dot(v1, v2)
            result = a_dot_b / abs_a_abs_b
            return result
    
    # convert titles in to term lists
    if len(t1) == 0 and len(t2) == 0:
        cos_sim = 1.0  # empty strings are absolutely the same for our cosine similarity score
    else:
        words = set()
        t1_terms = make_terms_from_string(t1,gram_filter,n)
        t2_terms = make_terms_from_string(t2,gram_filter,n)
        # add term lists to the set of known words
        words.update(t1_terms.keys())
        words.update(t2_terms.keys())
        # build dict of indexes from the word list (so we can index into our matrix)
        word_lookup = dict([(w, n) for (n, w) in enumerate(words)])
        # build 2 row matrix with nbr-of-words columns
        matrix = np.zeros((2, len(words)))
        # for each word, update the relevant row with the new word count
        for nd, d in enumerate([t1_terms, t2_terms]):
            #print nd, d
            for w in d:
                assert w in word_lookup  # if not present - we've got a bug!
                matrix[nd][word_lookup[w]] += d[w]#1
        cos_sim = __cosine_similarity(matrix[0], matrix[1])
    if cos_sim > 1.0 and cos_sim < 1.0000000005:
        cos_sim = 1.0  # round down if fractionally over 1.0
    if cos_sim < 0 or cos_sim > 1.0:
        print "Error in distance_cosine_measure"
        print t1
        print t2
        print cos_sim
    assert cos_sim >= 0 and cos_sim <= 1.0
    return 1.0 - cos_sim
