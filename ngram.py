# Michael Fitzgerald
# 02/13/2020 CMSC 416

# 1 - This program is designed to take in text files, either passed as cmd args
# or simply the defaults added by me, and break them down into sentences based on
# the given nGramSize and number of sentences within a given amount of time

# 2 - If given the sentences 'Hello my name is michael, what is your name? I want sponge cakes.'
# the program will output sentences like 'Hello my name I want sponge cakes. Michael what is your name.'
# this depends on nGramSize and number of sentences, which are parameters passed either via cmd
# or using the defaults I've set with this program

# 3 - detailed breakdown of the program
# get input parameters: nGramSize, numOfSentences, and text files to read
# do preprocessing on the corpus, putting all values to lowercase and removing stop tokens like commas
# use re.split to break the corpus into a list of all words appearing in the corpus by whitespace
# generate from the wordList a list of all unique tokens in the corpus
# go through the wordList word by word to find all nGrams and n-1 grams from the corpus
# get the number of times every n-1 gram appears in the corpus, and store those values in a dict as minusGram: count
# create a nested dicts for the nGram conditional probability table
# with each n-1 gram being the key to a dict of the following word
# and the number of times the full phrase appeared in the corpus
# With this table, we now create our sentences, starting with a number of starts equal to nGramSize -1
# we store each word into our wordHistory list, and use this wordHistory to search for the most probable token
# that follows the n-1 gram we got from our wordHistory
# we iterate through this process until the workingSentence has an '<end>' tag, at which point it ends and prints
# we do that a number of times equal to the numOfSentences parameter
# we then finish the execution of the program


import io
import random
import re
import sys


# begin function definitions

# This function will take the number of times the parameters as they are passed
# appear in the tokenList
# phrase is the preceding ngram
# word is the token following the phrase
# this function will return the probability of word given phrase
def nGramProbability(wholePhrase, gram):
    return float(wholePhrase / gram)


# begin main execution
def main():
    # get the passed parameters for the ngram number and the number of sentences
    if len(sys.argv) > 1:
        nGramSize = int(sys.argv[1])
        numOfSentences = int(sys.argv[2])
    else:
        nGramSize = 3
        numOfSentences = 10

    # import the text files
    corpus = ''

    starts = ''
    for i in range(nGramSize - 1):
        starts += '<start> '

    corpus += starts

    if len(sys.argv) > 3:
        print('We have text files to figure out!')
        for arg in sys.argv[3:]:
            corpus += (starts + arg)
    else:
        corpus += '"Hello", (World)!'

        file1 = io.open("TheChildrensBible.txt", encoding="utf-8")
        file2 = io.open("TheWeeOnesBible.txt", encoding="utf-8")
        file3 = io.open("TheWonderBook.txt", encoding="utf-8")

        data1 = file1.read()
        data2 = file2.read()
        data3 = file3.read()

        corpus += (starts + data1)
        corpus += (starts + data2)
        corpus += (starts + data3)

    # remove all capitalization
    corpus = corpus.lower()

    # remove parenthesis, single and double quotes, and commas
    corpus = re.sub('[(|)|,|"|;|:|_]', '', corpus)

    # remove punctuation and replace with the '<start>' and '<end>' tags
    corpus = re.sub('[.|?|!]', ' <end> <start> ', corpus)

    # convert \n into whitespace
    corpus = re.sub('\r\n', ' ', corpus)

    # create a list of all the tokens after the substitution of punctuation
    wordList = re.split('\s+', corpus)

    # find all unique tokens as well as the total number of tokens
    tokenList = list(dict.fromkeys(wordList))
    tokenList.remove('')

    # find all ngrams and n-1grams in the corpus
    nGramList = []
    minusGramList = []

    for i in range(len(wordList) - (nGramSize - 1)):
        nGram = ''
        minusGram = ''
        for j in range(0, nGramSize):
            word = wordList[i + j]
            nGram += word + ' '
        for k in range(0, nGramSize - 1):
            word = wordList[i + k]
            minusGram += word + ' '
        if nGram not in nGramList:
            nGramList.append(nGram)
        if minusGram not in minusGramList:
            minusGramList.append(minusGram)

    # create the n-1 gram dict and the ngram table
    minusGramFreq = dict()

    # get the count of every unique minusGram in the corpus
    for gram in minusGramList:
        count = corpus.count(gram)
        minusGramFreq.update({gram: count})

    # create the structure to store the probability of each potential word choice
    # use a function to process the probability for each ngram
    # store the probability into the data structure
    nGramProb = dict()

    for gram in minusGramList:
        gramProbDict = dict()
        gramCount = minusGramFreq.get(gram)
        for token in tokenList:
            phrase = gram + token
            phraseCount = corpus.count(phrase)
            if phraseCount is 0:
                break
            else:
                phraseProb = nGramProbability(phraseCount, gramCount) * 100
                gramProbDict.update({token: phraseProb})
        nGramProb.update({gram: gramProbDict})

    wordHistory = re.split('\s+', starts)
    wordHistory.remove('')

    # loop to create the sentences
    for i in range(numOfSentences):
        print('This is sentence ' + str(i + 1))
        sentenceComplete = False
        workingSentence = ''

        if i == 0:
            workingSentence += starts

        while sentenceComplete is not True:
            currentGram = ''

            for var in range(nGramSize - 1):
                currentGram += wordHistory[var] + ' '

            currentGramProbs = nGramProb.get(currentGram)
            nextWord = ''

            # if the currentGramProbs didn't naturally exist in the corpus
            # pick a random word from the wordIndex
            # otherwise get the next word based on the conditional probability
            if currentGramProbs is None:
                wordIndex = random.randrange(0, len(tokenList))
                nextWord = tokenList[wordIndex]
            else:
                nextWordProb = 0.0
                for token in tokenList:
                    tokenProb = currentGramProbs.get(token)
                    if tokenProb is None:
                        continue
                    elif tokenProb > nextWordProb:
                        nextWord = token

            # check if the wordHistory list is greater than the n-1 gram size
            # if it is, pop the first entry and append the new word
            # if not, just add the new word
            if len(wordHistory) > nGramSize - 1:
                wordHistory.pop(0)
                wordHistory.append(nextWord)
            else:
                wordHistory.append(nextWord)

            sentenceLength = len(re.split('\s+',workingSentence))

            # On the off chance the sentence can't or won't find a '<end>' tag,
            # auto cutoff sentences when it reaches 10 * the nGramSize
            if sentenceLength > 10 * nGramSize:
                workingSentence += (' ' + nextWord + ' <end>')
            else:
                workingSentence += ' ' + nextWord

            if '<end>' in workingSentence:
                sentenceComplete = True

        # remove the start and end tags from your sentence and print it out to the console
        workingSentence = re.sub('<end>', '.', workingSentence)
        workingSentence = re.sub('<start>', '', workingSentence)
        # substitute any strings of whitespace with a single space
        workingSentence = re.sub('\s+', ' ', workingSentence)
        # capitalize the sentence
        workingSentence = workingSentence.capitalize()
        print(workingSentence)

    print('Program Finished')

# end of program


if __name__ == '__main__':
    print('Program Start')
    main()
