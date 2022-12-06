#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system(' pip3 install selenium')


# In[ ]:


# importing standard libraries
import numpy as np
import pandas as pd
from collections import defaultdict

# Importing NLP libraries
import requests
import nltk
import re

# Importing Web_scraping Libraries
import selenium
from selenium import webdriver

# Importing the data.
data = pd.read_excel("Input.xlsx")
data.head()

# Importing stopwords.
nltk.download("stopwords")


from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))  # Since the paragraphs are in English.
stop_words = list(stop_words)

personal_pronouns = ["i", "me", "you", "he", "she", "it", "we", "us", "they", "them"]

# importing word list.
Word_list = pd.read_excel("LoughranMcDonald_MasterDictionary_2020.xlsx")
Word_list.head()


# Creating the list of positive, negative, and neutral words.
positive_words = []
negative_words = []
neutral_words = []
for i in range(0, len(Word_list) - 1):
    if Word_list["Negative"][i] > 0:
        negative_words.append(
            Word_list["Word"][i]
        )  # Negative and positive words are assigned values greater than 0.
    elif Word_list["Positive"][i] > 0:
        positive_words.append(Word_list["Word"][i])
    else:
        neutral_words.append(Word_list["Word"][i])


negative_words = [word for word in negative_words]
positive_words = [word for word in positive_words]

# webscraping
driver = webdriver.Chrome(
    "/Desktop/Untitled Folder 1/chromedriver.exe"
)

vowels = ["a", "e", "i", "o", "u"]


def Web_Scraper(data, positive, negative, stop_words, personal_pronouns, class_name):
    """
    Where,
    data: Main Data.
    positive: List of positive words.
    negative: List of negative words.
    stop_words: List of Stop words.
    personal_pronouns: List of personal pronouns.
    class_name: class name of the article
    """
    # Creating required variables.
    required_data = defaultdict(list)
    for url in data.URL:
        text_notes = []
        driver.get(url)
        temp = driver.find_element_by_class_name(class_name)
        for paragraph in temp.find_elements_by_tag_name("p"):
            text_notes.append(paragraph.text)
        #########################################################################################################
        """
        positive: Temporary variable assigned for number of positive words in the paragraph.
        negative: Temporary variable assigned for number of negative words in the paragraph.
        Polarity: Temporary variable assigned for the  polarity value.
        Subjectivity: Temporary variable assigned for the subjectivity value.
        """
        positive, negative, Polarity, subjectivity = Extracting_derived_variables(
            text_notes, positive_words, negative_words, stop_words
        )
        required_data["Positive_Score"].append(positive)
        required_data["Negative_Score"].append(negative)
        required_data["Polarity_score"].append(Polarity)
        required_data["Subjectivity_score"].append(subjectivity)
        #########################################################################################################
        """
        Avg_sent_length: Temporary variable for average length of the sentence.
        Percent_complex: Temporary variable for percent of complex words in the sentence.
        Avg_word_length: Temporary variable for average word length.
        """
        Avg_sent_length, Avg_words_per_sent, numb_sent = Analysis_of_readability(
            text_notes, positive_words, negative_words, stop_words
        )
        required_data["Average_sentence_length"].append(Avg_sent_length)
        required_data["Avg_word_length"].append(Avg_words_per_sent)
        required_data["Sentence_Score"].append(numb_sent)

        #########################################################################################################
        """
        word_count_bc: Temporary variable assigned for the word count before cleaning.
        word_count_ac: Temporary variable assigned for the word count after cleaning.
        syllable_count: Temporary variable assigned for the syllable count.
        personal_pronoun: Temporary variable assigned for the personal pronoun count.
        """
        word_count_bc, word_count_ac, syllable_count, personal_pronoun = Counts(
            text_notes, positive_words, negative_words, stop_words, personal_pronouns
        )
        required_data["words_before_cleaning"].append(word_count_bc)
        required_data["words_after_cleaning"].append(word_count_ac)
        required_data["Syllable_count"].append(syllable_count)
        required_data["Personal_pronoun_count"].append(personal_pronoun)

    # Converting the lists into the appropriate dataframes.
    return required_data


def Extracting_derived_variables(
    appended_list, positive_words, negative_words, stop_words
):

    sentence = "".join(map(str, appended_list)).lower()
    # Calculating the number of positive words.
    number_of_positive = len(
        [
            i
            for i in list(sentence.split(" "))
            if i in positive_words and i not in stop_words
        ]
    )
    # Calculating the number of negative words.
    number_of_negative = len(
        [
            i
            for i in list(sentence.split(" "))
            if i in negative_words and i not in stop_words
        ]
    )
    # calculating polarity score
    if number_of_positive == 0 and number_of_negative == 0:
        polarity_score = 0
    else:
        polarity_score = float(
            (number_of_positive - number_of_negative)
            / (number_of_positive + number_of_negative)
            + 0.000001
        )
    # calculating subjectivity score.
    number_of_words_after_cleaning = len(
        [i for i in list(sentence.split(" ")) if i not in stop_words]
    )
    subjectivity_score = float(
        (number_of_positive + number_of_negative) / number_of_words_after_cleaning
        + 0.000001
    )

    return number_of_positive, number_of_negative, polarity_score, subjectivity_score


def Analysis_of_readability(appended_list, positive_words, negative_words, stop_words):
    sentence = "".join(map(str, appended_list)).lower()
    # Calculating the number of sentences.
    number_of_sentences = len(list(sentence.split(".")))
    # calculating average sentence length.
    number_of_words_after_cleaning = len(
        [i for i in list(sentence.split(" ")) if i not in stop_words]
    )
    avg_sentence_len = float(number_of_words_after_cleaning / number_of_sentences)
    # calculating number of words per sentence
    number_of_words_before_cleaning = len([i for i in list(sentence.split(" "))])
    avg_words_per_sent = float(number_of_words_before_cleaning / number_of_sentences)
    return avg_sentence_len, avg_words_per_sent, number_of_sentences


def Counts(
    appended_list, positive_words, negative_words, stop_words, personal_pronouns
):
    vowels = ["a", "e", "i", "o", "u"]
    sentence = "".join(map(str, appended_list)).lower()
    # calculating number of personal pronouns.
    number_of_personal_pronouns = len(
        [i for i in list(sentence.split(" ")) if i in personal_pronouns]
    )
    # Syllable_count
    Syllable_count = 0
    for words in list(sentence):
        Syllable_count += len([alphabet for alphabet in words if alphabet in vowels])
    # Calculating number of words before removing the stop_words.
    number_of_words_before_cleaning = len([i for i in list(sentence.split(" "))])
    # Calculating number of words after removing the stop_words.
    number_of_words_after_cleaning = len(
        [i for i in list(sentence.split(" ")) if i not in stop_words]
    )
    return (
        number_of_words_before_cleaning,
        number_of_words_after_cleaning,
        Syllable_count,
        number_of_personal_pronouns,
    )

if __name__ == "__main__":
    updated_dataframe = Web_Scraper(
        data,
        positive_words,
        negative_words,
        stop_words,
        personal_pronouns,
        "td-post-content",
    )

    updated_dataframe.to_csv("Black_coffer_Assignment")

