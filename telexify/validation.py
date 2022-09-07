from __future__ import unicode_literals
import collections
from . import tone, mark, utils
Tone = tone.Tone


CONSONANTS = set([
    'b', 'c', 'ch', 'd', 'g', 'gh', 'gi', 'h', 'k', 'kh', 'l', 'm', 'n', 'ng',
    'ngh', 'nh', 'p', 'ph', 'qu', 'r', 's', 't', 'th', 'tr', 'v', 'x', 'đ'
])

TERMINAL_CONSONANTS = set([
    'c', 'ch', 'm', 'n', 'ng', 'nh', 'p', 't'
])

VOWELS = set([
    'a', 'ai', 'ao', 'au', 'ay', 'e', 'eo', 'i', 'ia', 'iu', 'iê', 'iêu',
    'o', 'oa', 'oai', 'oao', 'oay', 'oe', 'oeo', 'oi', 'oo', 'oă', 'u', 'ua',
    'ui', 'uy', 'uya', 'uyu', 'uyê', 'uâ', 'uây', 'uê', 'uô', 'uôi',
    'uơ', 'y', 'yê', 'yêu', 'â', 'âu', 'ây', 'ê', 'êu', 'ô', 'ôi',
    'ă', 'ơ', 'ơi', 'ư', 'ưa', 'ưi', 'ưu', 'ươ', 'ươi', 'ươu'
])

TERMINAL_VOWELS = set([
    'ai', 'ao', 'au', 'ay', 'eo', 'ia', 'iu', 'iêu', 'oai', 'oao', 'oay',
    'oeo', 'oi', 'ua', 'ui', 'uya', 'uyu', 'uây', 'uôi', 'uơ', 'yêu', 'âu',
    'ây', 'êu', 'ôi', 'ơi', 'ưa', 'ưi', 'ưu', 'ươi', 'ươu'
])

STRIPPED_VOWELS = set(map(mark.strip, VOWELS))

# 'uo' may clash with 'ươ' and prevent typing 'thương'
# 'ua' may clash with 'uâ' and prevent typing 'luật'
STRIPPED_TERMINAL_VOWELS = \
    set(map(mark.strip, TERMINAL_VOWELS)) - set(['uo', 'ua'])


SoundTuple = \
    collections.namedtuple('SoundTuple', ['first_consonant', 'vowel', 'last_consonant'])


def is_valid_string(string, final_form=True):
    return is_valid_combination(utils.separate(string), final_form)


def is_valid_combination(comp, final_form=True):
    return is_valid_sound_tuple(comp, final_form)


def is_valid_sound_tuple(sound_tuple, final_form=True):
    """
    Check if a character combination complies to Vietnamese phonology.
    The basic idea is that if one can pronunce a sound_tuple then it's valid.
    Sound tuples containing consonants exclusively (almost always
    abbreviations) are also valid.

    Input:
        sound_tuple - a SoundTuple
        final_form  - whether the tuple represents a complete word
    Output:
        True if the tuple seems to be Vietnamese, False otherwise.
    """

    # We only work with lower case
    sound_tuple = SoundTuple._make([s.lower() for s in sound_tuple])

    # Words with no vowel are always valid
    # FIXME: This looks like it should be toggled by a config key.
    if not sound_tuple.vowel:
        result = True
    elif final_form:
        result = \
            has_valid_consonants(sound_tuple) and \
            has_valid_vowel(sound_tuple) and \
            has_valid_tone(sound_tuple)
    else:
        result = \
            has_valid_consonants(sound_tuple) and \
            has_valid_vowel_non_final(sound_tuple)

    return result


def has_valid_consonants(sound_tuple):

    def has_invalid_first_consonant():
        return (sound_tuple.first_consonant != "" and
                not sound_tuple.first_consonant in CONSONANTS)

    def has_invalid_last_consonant():
        return (sound_tuple.last_consonant != "" and
                not sound_tuple.last_consonant in TERMINAL_CONSONANTS)

    return not (has_invalid_first_consonant() or
                has_invalid_last_consonant())


def has_valid_vowel_non_final(sound_tuple):
    # If the sound_tuple is not complete, we only care whether its vowel
    # position can be transformed into a legit vowel.

    stripped_vowel = mark.strip(sound_tuple.vowel)
    if sound_tuple.last_consonant != '':
        return stripped_vowel in STRIPPED_VOWELS - STRIPPED_TERMINAL_VOWELS
    else:
        return stripped_vowel in STRIPPED_VOWELS


def has_valid_vowel(sound_tuple):
    # Check our vowel.
    # First remove all tones
    vowel_wo_tone = tone.remove_tone_string(sound_tuple.vowel)

    def has_valid_vowel_form():
        return vowel_wo_tone in VOWELS and not \
            (sound_tuple.last_consonant != '' and
                vowel_wo_tone in TERMINAL_VOWELS)

    def has_valid_ch_ending():
        # 'ch' can only go after a, ê, uê, i, uy, oa
        return not (sound_tuple.last_consonant == 'ch' and
                    not vowel_wo_tone in
                    ('a', 'ê', 'uê', 'i', 'uy', 'oa'))

    def has_valid_c_ending():
        # 'c' can't go after 'i' or 'ơ'
        return not (sound_tuple.last_consonant == 'c' and
                    vowel_wo_tone in ('i', 'ơ'))

    def has_valid_ng_ending():
        # 'ng' can't go after i, ơ
        return not (sound_tuple.last_consonant == 'ng' and
                    vowel_wo_tone in ('i', 'ơ'))

    def has_valid_nh_ending():
        # 'nh' can only go after a, ê, uy, i, oa, quy
        has_y_but_is_not_quynh = vowel_wo_tone == 'y' and \
            sound_tuple.first_consonant != 'qu'

        has_invalid_vowel = not vowel_wo_tone in \
            ('a', 'ê', 'i', 'uy', 'oa', 'uê', 'y')

        return not \
            (sound_tuple.last_consonant == 'nh' and
                (has_invalid_vowel or has_y_but_is_not_quynh))

    # The ng and nh rules are not really phonetic but spelling rules.
    # Including them may hinder typing freedom and may prevent typing
    # unique local names.
    return \
        has_valid_vowel_form() and \
        has_valid_ch_ending() and \
        has_valid_c_ending()
        # has_valid_ng_ending() and \
        # has_valid_nh_ending()


def has_valid_tone(sound_tuple):
    akzent = tone.get_tone_string(sound_tuple.vowel)

    # These consonants can only go with ACUTE, DOT tones
    return not (sound_tuple.last_consonant in ('c', 'p', 't', 'ch') and
                not akzent in (Tone.ACUTE, Tone.DOT))