__author__ = 'Simone Mainardi, simonemainardi@startmail.com'

import codecs
from word import Word
from database.storage import storage


def prepender(func):
    """
    Prepends some text to the *second* argument with which function `func` has been called.
    The *first* argument is a reference (`self`) to an instance of class Terms or one of its sub classes.
    `self` is accessed to look for a prefix `_prefix` to append to the second argument.

    This function is meant to be used as decorator.
    """
    def prepend(self, *args):
        prepended = self._prefix + args[0]
        return func(self, prepended, *args[1:])
    return prepend

def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text
    else:
        return text.decode('utf-8') 
class Terms(object):
    def __init__(self, store=None):
        self._items = store

    @property
    def terms(self):
        """
        Returns all the terms we have stored without their prefix
        """
        return [k[len(self._prefix):] for k in self._items.keys() if k.startswith(self._prefix)]


class OriginalTerms(Terms):
    _prefix = 't:'  # this prefix stands for `term:`

    @prepender
    def __setitem__(self, word, count):
        """
        Adds the `word` to the original terms. The number of occurrences is specified in `count`.
        """
        self._items.incrby(word, count)

    @prepender
    def __getitem__(self, word):
        """
        Returns the number of occurrences of `word` in the corpus or 0 if it wasn't present.
        """
        return self._items[word] if word in self._items else 0


class SuggestTerms(Terms):
    _prefix = 's:'  # this prefix stands for `suggestion:`

    def __init__(self, store, best_suggestions_only=True):
        self._best_suggestions_only = best_suggestions_only
        super(SuggestTerms, self).__init__(store)

    @prepender
    def __setitem__(self, delete, suggestion):
        """
        Adds the `delete` term with the corresponding `suggestion`.
        """
        # Damerau-Levenshtein distance can be trivially inferred since `delete` is obtained
        # by deleting one or more characters from suggestion.
        suggestions = self._items.smembers(delete)  # get currently existing suggestions
        smallest_suggestion_len = len(min(suggestions, key=len)) if suggestions else len(suggestion)
        if len(suggestion) < smallest_suggestion_len and self._best_suggestions_only:
            # if the new suggestion` has a smaller Damerau-Levenshtein distance from `delete`
            # we clear the already existing suggestions
            # The new `suggestion` has a smaller Damerau-Levenshtein distance if:
            # len(suggestion) - len(delete) < len(min(suggestions, key=len)) - len(delete)
            # if we simplify on len(delete) on both sides, we obtain the second condition in the above if statement.
            self._items.sclear(delete)
        if not self._best_suggestions_only or len(suggestion) <= smallest_suggestion_len:
            self._items.sadd(delete, suggestion)

    @prepender
    def __getitem__(self, word):
        return self._items.smembers(word)


class Dictionary(object):
    def __init__(self, edit_distance_max=2, best_suggestions_only=True, storage_type=None, **kwargs):
        store = storage(storage_type, **kwargs)
        self._terms = OriginalTerms(store)
        self._suggestions = SuggestTerms(store, best_suggestions_only)
        self.edit_distance_max = edit_distance_max
        self.best_suggestions_only = best_suggestions_only

    def add_word(self, word):
        self._terms[word] = 1
        for delete in Word.deletes(word, self.edit_distance_max):
            self._suggestions[delete] = word

    def add_words(self, words):
        for word in words:
            self.add_word(word)

    def initialize(self, text):
        """ Initializes the dictionary using the `text` provided.
        """
        with codecs.open(text, encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                self.add_word(word)

    def lookup(self, word, return_distances=False):
        results = set()
        candidates = set([(word, 0)])  # a set of tuples (candidate, candidate_distance)
        for delete in Word.deletes(word, self.edit_distance_max):
            delete_distance = len(word) - len(delete)
            candidates.update([(delete, delete_distance)])
        candidates = sorted(candidates, key=lambda x: x[1])  # sort by increasing distance
        while candidates:
            candidate, candidate_distance = candidates.pop()  # the distance of the candidate from `word`
            candidate_count = self._terms[candidate]  # the (possibly 0) no. of occurrences for candidate
            if candidate_count > 0:  # there is an entry for this item in the dictionary
                #  candidate is an original word!
                results.update([(candidate, candidate_distance)])
            suggestions = self._suggestions[candidate]  # the (possibly not existing) suggestions for candidate
            for suggestion in suggestions:
                if not safe_unicode(suggestion) in [safe_unicode(r[0]) for r in results]:  # the sugg. exists and hasn't been found yet
                    if safe_unicode(suggestion) == safe_unicode(word):  # suggestion _is_ the word we are looking for
                        real_distance = 0
                    elif candidate_distance == 0:  # candidate _is_ the word we are looking up for
                        real_distance = len(suggestion) - len(candidate)  # suggestion_distance
                    else:  # candidate is a delete edit of the word we are looking up for
                        real_distance = Word.damerau_levenshtein_distance(word, suggestion)
                    if real_distance <= self.edit_distance_max:
                        results.update([(suggestion, real_distance)])
        # sort the results first by increasing distance, then by decreasing frequency
        results = sorted(list(results), key=lambda r: (r[1], -self._terms[r[0]]))
        if self.best_suggestions_only and len(results) > 1:
            # only take the original word (if present) and the suggestions with minimum distance from `word`
            min_index = 0 if results[0][1] != 0 else 1  # possibly exclude `word` from the minimum distance
            best_dist = min(results[min_index:], key=lambda r: r[1])[1]  # results[0] may be the original word
            results = [r for r in results if r[1] <= best_dist]
        if not return_distances:
            results = [r[0] for r in results]  # pop out the distances and keep only the suggestions
        return results


if __name__ == '__main__':
    pass
