#-*- coding: utf-8 -*-
import codecs
import re

import textblob_aptagger
from textblob import Word



pt = textblob_aptagger.PerceptronTagger()


def lemmatize_query(query):
    lemmatised = []
    for surface_word in query.split():
        lemma = Word(surface_word).lemmatize()
        lemmatised.append(lemma)
        # Hack. Now we don't have POSs anymore, we must check whether
        # the word might be an irregular verb ('was', 'would')
        lemma_verb = Word(surface_word).lemmatize('v')
        if lemma_verb != lemma:
            # Only include if different. So 'calls' (plural noun or 3.sing verb)
            # would end up with just one mention
            lemmatised.append(lemma_verb)

    return ' '.join(lemmatised)


def tag_query(query):
    tagged = []
    for surface, pos in pt.tag(query):
        if pos[0] in ('N', 'V'):
            tag = '{}_{}'.format(Word(surface).lemmatize(pos[0].lower()), pos[0])
        elif pos[0] == 'J':
                # Hack -- convert pos J to pos A because that's how
                # adjectives are represented in dm file
            tag = '{}_A'.format(Word(surface).lemmatize().lower())
        else:
            tag = '{}_{}'.format(Word(surface).lemmatize().lower(), pos[0])
        tagged.append(tag)

    return ' '.join(tagged)


def write_tagged_file(input_file, output_file):
    url_info = ''
    first_line = True

    with codecs.open(input_file, 'r', encoding='utf-8') as text:
        tmpline, text_lines = "", []
        for line in text:
            line = line.strip()
            if first_line and line.startswith('#'):  # If first line with URL info
                url_info = line
                first_line = False
            else:
                # Add some pre-processing here (boilerplate removal, etc)
                line = line.replace('^', '')
                # Remove links, marked by a * in lynx
                if not re.search('^\s+\*', line):
                    if re.search('\.\s*$', line):  # end of sentence
                        tmpline += " " + line
                        text_lines.append(line)
                        tmpline = ""
                    else:
                        tmpline += " " + line

    with open(output_file, 'w') as text_out:
        text_out.write('{}\n'.format(url_info))
        for line in text_lines:
            tagged = []
            line = line.strip()
            for surface, pos in pt.tag(line):
                if pos[0] in ('N', 'V'):
                    tagged.append('{}_{}'.format(Word(surface).lemmatize(pos[0].lower()), pos))
                else:
                    tagged.append('{}_{}'.format(Word(surface).lemmatize().lower(), pos))

            tagged_line = ' '.join(tagged)
            tagged_line = tagged_line.encode('utf8', 'replace')
            text_out.write('{}\n'.format(tagged_line))


if __name__ == '__main__':
    import sys
    write_tagged_file(sys.argv[1], sys.argv[2])
