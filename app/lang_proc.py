import codecs
import re

import textblob_aptagger
from textblob import Word, wordnet



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


def tagQuery(query):
    taggedquery = ""
    try:
        tags = pt.tag(query)
        if len(tags) > 0:
            for word in tags:
                surface = word[0]
                pos = word[1]
                try:
                    if pos[0] == 'N' or pos[0] == 'V':
                        tag = Word(surface).lemmatize(
                                pos[0].lower()) + "_" + pos[0]
                    else:
                        if pos[0] == 'J':
                            # Hack -- convert pos J to pos A because that's how
                            # adjectives are represented in dm file
                            tag = Word(surface).lemmatize().lower() + "_A"
                        else:
                            tag = Word(surface).lemmatize(
                            ).lower() + "_" + pos[0]
                    taggedquery = taggedquery + tag + " "
                except:
                    taggedquery = taggedquery + surface + "_" + pos[0] + " "
    except:
        print "ERROR processing query", query
    return taggedquery


def runScript(f1, f2):
    text = codecs.open(f1, 'r', encoding='utf-8')
    text_out = open(f2, 'w')
    text_lines = []
    tmpline = ""

    c = 0  # Line counter, just to check on the first line
    for line in text:
        line = line.rstrip('\n')
        if c == 0 and line[0] == '#':  # If first line with URL info
            text_out.write(line + '\n')
            c += 1
        else:
            # Add some pre-processing here (boilerplate removal, etc)
            line = line.replace('^', '')
            # Remove links, marked by a * in lynx
            m = re.search('^\s+\*', line)
            m2 = re.search('^\s+\+', line)
            m3 = re.search('\.\s*$', line)  # Find end of sentence
            if not m and line != "\n":
                if m3:
                    tmpline = tmpline + " " + line
                    text_lines.append(tmpline)
                    tmpline = ""
                else:
                    tmpline = tmpline + " " + line
    text.close()

    for l in text_lines:
        taggedline = ""
        l = l.rstrip('\n')
        try:
            tags = pt.tag(l)
            if len(tags) > 0:
                for word in tags:
                    surface = word[0]
                    pos = word[1]
                    try:
                        if pos[0] == 'N' or pos[0] == 'V':
                            tag = Word(surface).lemmatize(
                                    pos[0].lower()) + "_" + pos
                        else:
                            tag = Word(surface).lemmatize().lower() + "_" + pos
                        taggedline = taggedline + tag + " "
                    except:
                        taggedline = taggedline + surface + "_" + pos + " "
        except:
            print "ERROR processing line", l

        to_print = taggedline.encode('utf8', 'replace') + "\n"
        text_out.write(to_print)
    text_out.close()
