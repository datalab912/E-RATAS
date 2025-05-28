import numpy as np
import spacy
import networkx as nx
from scipy import spatial
from keybert import KeyBERT
import nltk
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import wordnet


#Function that is used to create a keyword dictionary for finding keywords within a paragraph
def title_func(title, topic_idea):
  nlp = spacy.load("en_core_web_sm")
  topic_based_dict = {
      "Web Development": {"JavaScript": 1.0, "React": 1.0, "HTML": 1.0, "CSS": 1.0, "User Experience": 1.0, "Website": 1.0},
      "Machine Learning": {"Prediction": 1.0, "Model": 1.0, "Regression": 1.0, "Classification": 1.0, "Architecture": 1.0, "BERT": 2.0},
      "Large Language Models": {"BERT": 2.0, "Neural Network": 1.0, "Convolutional": 1.0, "CNN": 1.0, "Transformers": 1.0, "Model": 1.0, "Large Language Model": 1.0},
      "Sample Title Check": {"task": 3.0, "conclusion": 3.0, "result": 2.0, "assigned": 2.0}
  }
  if topic_idea in topic_based_dict.keys():
    IT_keywords = topic_based_dict[topic_idea]

  title_doc = nlp(title)
  title_graph = nx.Graph()
  for token in title_doc:
    title_graph.add_node(token.text)
    for child in token.children:
      title_graph.add_edge(token.text, child.text)

  score = {word.text: IT_keywords.get(word.text, 1.0) for word in title_doc if not word.is_stop and not word.is_punct}

  sorted_keywords = sorted(score, key = score.get, reverse= True)
  top_keywords = sorted_keywords[:5]
  return top_keywords

def library_sample_check_function_new_sentence_model(library_sample_check_list, title):
    model = SentenceTransformer('all-mpnet-base-v2')
    title_encoded = model.encode(title)
    paragraph_dict = {}
    for paragraph in library_sample_check_list:
        paragraph_encoded = model.encode(paragraph)
        similarity_score = round(util.pytorch_cos_sim(title_encoded, paragraph_encoded).item() * 100)
        paragraph_dict[paragraph] = similarity_score
    return paragraph_dict

#Function to extract multi word keywords from the title which is provided
def extract_keywords_with_diversity(title):
    model = KeyBERT("all-mpnet-base-v2")
    keywords = model.extract_keywords(title, keyphrase_ngram_range = (2,2), stop_words = "english", use_maxsum = True, nr_candidates = 6, top_n = 5)
    return keywords

#Function to extract keywords from the title which is provided.
def extract_keywords(title):
    model = KeyBERT("all-mpnet-base-v2")
    keywords = model.extract_keywords(title)
    return keywords

def synonym_function(keyword):
    synonym_list = []
    for word in wordnet.synsets(keyword):
        for lemma in word.lemmas():
            if lemma.name() != keyword:
                synonym_list.append(lemma.name())
    return synonym_list

#Function which checks how many keywords and/or its synonym(s) are used in the top 3 paragraphs
#Percentages are calculated based on how many keywords and their synonym is mentioned divided by the sum of the scores.
def list_analysis(further_analysis_list, keywords):
    target_counter = round(sum(keyword[-1] for keyword in keywords),3)
    difference_val = {}
    for paragraph in further_analysis_list.keys():
        word_counter = 0
        unique_list = []
        for keyword in keywords:
            synonym_list = synonym_function(keyword[0])
        for word in synonym_list:
            if word in paragraph and keyword[0] not in unique_list:
                word_counter += keyword[-1]
            unique_list.append(keyword[0])
        if keyword[0] not in unique_list and keyword[0] in paragraph:
            word_counter += keyword[-1]
            unique_list.append(keyword[0])
        word_counter = round((word_counter/target_counter) * 100)
        difference_val[paragraph] = word_counter
    return difference_val


#Function to keep 3 paragraphs that have the highest context similarity score
def result_analysis(paragraph_dict, title):
    further_analysis_dict = {key: value for key, value in sorted(paragraph_dict.items(), key=lambda x: x[1], reverse=True)[:3]}
    return further_analysis_dict

#Function to determine the overall percentage of a paragraph and how it is related to the title.
def score_avgs(final_draft_list, result_analysis_list):
    list_dict = {}
    for paragraph in final_draft_list.keys():
        updated_keyword_score = final_draft_list[paragraph] * 0.4
        updated_context_score = result_analysis_list.get(paragraph,0) * 0.6 * 2
        updated_final_score = updated_keyword_score + updated_context_score
        list_dict[paragraph] = round(normalize_score(round(updated_final_score,1)),1)

    return list_dict

#Function to normalise scores that have reached over 100%
def normalize_score(score):
    normalized_score = min(99, score)
    return normalized_score

def calculate_score(paragraph_list, title):
    #Function to check context similarity between a title and respective paragraph

    #Performing context similarity check with all paragraph lists.
    library_list = [paragraph_list]
    library_sentence_transformer_list = []
    for list_var in library_list:
        library_sentence_transformer_list.append(library_sample_check_function_new_sentence_model(list_var, title))

    #Calling the function within a variable to store the keywords from a title
    extracted_keywords = extract_keywords(title)


    #Calling the multi word keywords function.
    keywords = extract_keywords_with_diversity(title)
    sum_val = round(sum(keyword[-1] for keyword in keywords),3)

    #Calling the result_analysis function
    result_analysis_list = []
    for val in library_sentence_transformer_list:
        result_analysis_list.append(result_analysis(val, title))
    print('length of result_analysis_list', len(result_analysis_list[0]))


    #Calling of list_analysis for all top 3 paragraphs from all lists.
    final_draft_list = []
    for dictionary in result_analysis_list:
        final_draft_list.append(list_analysis(dictionary, extracted_keywords))

    result = []

    for val, val_1 in zip(final_draft_list, result_analysis_list):
        result.append(score_avgs(val, val_1))

    return result

#List of paragraphs from different documents from university students and a title to test with for context and keyword similarities.

paragraph_and_score = []


with open('paragraph_from_pdf.txt', 'r') as file:
    paragraph_list = file.readlines()[:100] 
    print(len(paragraph_list))
    print(paragraph_list[:10])
    title = "Provide a detailed description of the project conducted during the internship and its overall expectations."
    paragraph_and_score = calculate_score(paragraph_list, title)

print(paragraph_and_score[:10])
print(len(paragraph_and_score[0]))

with open('paragraph_and_score_algo.txt', 'a') as file:
    for pas in paragraph_and_score:
        for paragraph, score in pas.items():
            file.write(f'{paragraph},{score}\n')