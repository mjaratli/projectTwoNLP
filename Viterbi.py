import math
import string
import collections
import sys


# Helps split elements when processing the train and test file
def split_elements(element):
    # If statement to split these occurrences in training file: 1\/2/CD
    backslash = '\\'
    if backslash in element:
        index = element.rfind('/')
        word = element[0:index]
        tag = element[index + 1:len(element)]
    # Else to split the other, more common, occurrences in training file: The/DT
    else:
        element = element.split('/')
        word = element[0]
        tag = element[1]

    return word, tag


# Grabbing counts from the train file
def process_train(fileName):
    # Count of words and start of sentences and their corresponding tags. Ex. Play,Verb 50
    word_tag = collections.Counter()
    # Count of two tags. Ex. Noun,Verb 25
    two_tags = collections.Counter()
    # Count of tags and start of sentences. Ex. Verb 300
    tags = collections.Counter()

    # Opening the file to grab the counts
    with open(fileName, 'r') as trainFile:
        # Element is each line
        for line in trainFile:
            # Split line by space delimiter into an array
            eachLine = line.split()
            # Grab elements in array one by one and get the necessary counts
            for index, element in enumerate(eachLine):
                if index < len(eachLine) - 1:
                    current_element = (eachLine[index])
                    next_element = (eachLine[index + 1])
                    current_word, current_tag = split_elements(current_element)
                    next_word, next_tag = split_elements(next_element)
                    # Tags
                    tags[current_tag] += 1
                    # Two tags
                    two_tags_input = (f"{current_tag}", f"{next_tag}")
                    two_tags[two_tags_input] += 1
                    # Word tag
                    word_tag_input = (f"{current_word}", f"{current_tag}")
                    word_tag[word_tag_input] += 1

                    # Ensures that the last tag ./. is accounted for
                    if index + 2 == len(eachLine):
                        # Tags
                        tags[next_tag] += 1
                        # Word tag
                        word_tag_input = (f"{next_word}", f"{next_tag}")
                        word_tag[word_tag_input] += 1

                    # Ensures that SOF (Start of sentence) is accounted for
                    if index == 0:
                        # Tags SOF (Start of sentence)
                        tags['SOF'] += 1
                        # Two tags SOF (Start of sentence)
                        two_tags_input = (f"{'SOF'}", f"{current_tag}")
                        two_tags[two_tags_input] += 1

        return word_tag, two_tags, tags


def collect_prob(word_tag_p, two_tags_p, tags_p):
    # Lexical probabilities. Ex. P(hello given NN) = 0.01
    lexical_prob = {}
    # Calculating the lexical probabilities
    for keyOne, keyTwo in word_tag_p:
        lexical_input = (f"{keyOne}", f"{keyTwo}")
        count_tag_word = word_tag_p[keyOne, keyTwo]
        count_tag = tags_p[keyTwo]
        lexical_prob[lexical_input] = count_tag_word / count_tag

    # Bigram probabilities. Ex. P(VB given NN) = 0.29
    bigram_prob = {}
    # Calculating the bigram probabilities
    for keyOne, keyTwo in two_tags_p:
        bigram_input = (f"{keyOne}", f"{keyTwo}")
        count_tag_tag = two_tags_p[keyTwo, keyOne]
        count_tag = tags_p[keyTwo]
        bigram_prob[bigram_input] = count_tag_tag / count_tag

    return bigram_prob, lexical_prob


# Call the text pre-processing function and return a processed list
arg = " "
arg2 = " "

if len(sys.argv) >= 2:
    arg = sys.argv[1]

if len(sys.argv) >= 3:
    arg2 = sys.argv[2]

# Process the training file and collect all the counts necessary for determining probabilities
word_tag_result, two_tags_result, tags_result = process_train(arg)
# Calculate the bigram P(N given V) probabilities and the lexical P(a given DT) probabilities
bigram_probabilities, lexical_probabilities = collect_prob(word_tag_result, two_tags_result, tags_result)
