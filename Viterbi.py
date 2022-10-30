import math
import string
import collections
import sys


# # Grab the tags that can potentially occur per word in the line
# tags_per_word = []
# for element in line:
#     tags_per_element = [element]
#     for keyOne, keyTwo in lex_prob:
#         if keyOne == element:
#             tags_per_element.append(keyTwo)
#     # If there are no tags, default tag is Noun (NN)
#     if len(tags_per_element) == 1:
#         tags_per_element.append('NN')
#     tags_per_word.append(tags_per_element)

# # Store the tags of the current word
#             prev_tags = []
#             if col > 0:
#                 prev_tags.append(tags_per_word[row][col])
class Word:
    def __init__(self, word, tag, score, backptr):
        self.word = word
        self.tag = tag
        self.score = score
        self.backptr = backptr


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
        bigram_input = (f"{keyTwo}", f"{keyOne}")
        count_tag_tag = two_tags_p[keyOne, keyTwo]
        count_tag = tags_p[keyTwo]
        bigram_prob[bigram_input] = count_tag_tag / count_tag

    return bigram_prob, lexical_prob


def viterbi(bi_prob, lex_prob, line):
    # Grab the tags that can potentially occur per word in the line
    tags_per_word = []
    for element in line:
        tags_per_element = [element]
        tags_per_element += [keyTwo for keyOne, keyTwo in lex_prob if keyOne == element]
        if len(tags_per_element) == 1:
            tags_per_element.append('NN')
        tags_per_word.append(tags_per_element)

    # The final array is a 2 dimensional array with each element containing
    # word, tag, score, and a back-ptr
    fa_element = []
    final_array = []

    for row in range(len(tags_per_word)):
        # Reset the fa_element
        fa_element = []
        # Assigning the word to each element
        word = tags_per_word[row][0]
        fa_element.append(word)
        for col in range(len(tags_per_word[row])):
            score = 0
            # Initialization step : If it is the first word
            if row == 0 and col > 0:
                backptr = 0
                tag = tags_per_word[row][col]
                # l_prob = lex_prob.get([word, tag], 0)
                # b_prob = bi_prob.get([tag, 'SOF'], 0)
                try:
                    score = math.log2(lex_prob[word, tag] + 1) * math.log2(bi_prob[tag, 'SOF'] + 1)
                except KeyError:
                    score = 1
                fa_element.append(tag)
                fa_element.append(score)
                fa_element.append(backptr)
                final_array.append(fa_element)
            # Iteration step
            if row > 0 and col > 0:
                prev_tags = tags_per_word[row - 1][1:]
                # Need to change this to a dictionary
                previous_score = final_array[row - 1][2]
                current_tag = tags_per_word[row][col]
                try:
                    tagt_given_tagj = bi_prob[current_tag, prev_tags[0]]
                except KeyError:
                    tagt_given_tagj = 1
                max_score = math.log2(previous_score + 1) * math.log2(tagt_given_tagj + 1)
                backptr = prev_tags[0]

                for prev_tag in prev_tags:
                    try:
                        tagt_given_tagj = bi_prob[current_tag, prev_tag]
                    except KeyError:
                        tagt_given_tagj = 1
                    max_score_compare = math.log2(previous_score + 1) * math.log2(tagt_given_tagj + 1)
                    if max_score < max_score_compare:
                        max_score = max_score_compare
                        backptr = prev_tag

                fa_element.append(current_tag)
                try:
                    prob_word_given_tag = math.log2(lex_prob[word, current_tag] + 1)
                except KeyError:
                    prob_word_given_tag = 1
                score = prob_word_given_tag * max_score
                fa_element.append(score)
                fa_element.append(backptr)
                final_array.append(fa_element)

            fa_element = fa_element[:1]

    return 0

    # # Initialization step
    # for index, element in enumerate(tags_per_word[0]):
    #     firstWord = tags_per_word[0][0]
    #     fa_element.append(firstWord)
    #     fa_element.append(tags_per_word[0][index])
    #     hi = 5


def process_test(bigram_p, lexical_p, fileName):
    predictions = []
    # tagValues grabs the gold standard tags from each line while tagValuesGS is the gold standard tag values for the
    # entire test file
    tagValuesGS = []

    # Opening the test file to grab line by line
    with open(fileName, 'r') as testFile:
        # Grab each line
        for line in testFile:
            # Split line by space delimiter into an array
            eachLine = line.split()
            tagValues = []
            # Remove the tags from each element, store the tags, and update eachLine to only hold the words of the line
            for index, element in enumerate(eachLine):
                if index < len(eachLine):
                    word, tag = split_elements(element)
                    eachLine[index] = word
                    tagValues.append(tag)
            tagValuesGS.append(tagValues)
            # Run the viterbi algorithm on each line
            viterbi(bigram_p, lexical_p, eachLine)

    return predictions


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
# Run the Viterbi Algorithm
predicted_tags = process_test(bigram_probabilities, lexical_probabilities, arg2)
