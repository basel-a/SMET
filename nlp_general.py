"""
Created on Wed Mar 18 12:15:21 2020

@author: babdeen
"""
import spacy

import numpy as np
from spacy.lang.en import English
parser = spacy.load("en_core_web_lg",disable=['ner'])
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

stop_words = stop_words.union(['may','should','can','could'])

sw_NN = set(list(stop_words)+['part','kind','different','number','all','many','kinds','parts','whole','certain','various','other','such','both','multiple','some','several'])
import string
from nltk.corpus import wordnet as wn
import re
from collections import Counter,OrderedDict
import pickle
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from sklearn.feature_extraction.text import TfidfVectorizer
from pattern.en import lexeme, pluralize
from numpy.linalg import norm
from numpy import dot


class NLP:
    def srl_to_dict(srl):
        SRLDict = {}
        for verb in srl['verbs']:
            verb_str = verb['id']
            SRLDict[verb_str] = {}
            for ind,tag in enumerate(verb['tags']):
                if tag != 'O':
                    if tag[0] == 'B':
                        newTag = tag[tag.find('-')+1:]
                        if newTag not in SRLDict[verb_str]:
                            SRLDict[verb_str][newTag] = {'text': srl['words'][ind] }
                        else:
                            SRLDict[verb_str][newTag]['text'] += ('/ ' + srl['words'][ind]) 
                        if newTag == 'V':
                            SRLDict[verb_str][newTag]['index'] = ind
                    else :   
                        newTag = tag[tag.find('-')+1:]
                        if newTag not in SRLDict[verb_str]:
                            continue
                        SRLDict[verb_str][newTag]['text'] += (' ' + srl['words'][ind]) 
    
        return SRLDict
    def add_v_id_srl_from_dict(srls):
        for srl in srls:
            NLP.add_v_id_srl(srls[srl])
            
    def srl_to_dict_from_dict(srls):
        return {srl:NLP.srl_to_dict(srls[srl]) for srl in srls}
    def add_v_id_srl(srl):
        verbs = set()
        counter = {}
    
        for v in srl["verbs"]:
            if v["verb"] not in verbs:
                verbs.add(v["verb"])
                counter[v["verb"]] = 1
                v['id'] = v["verb"] 
            else:
                counter[v["verb"]] += 1
                v['id'] = v["verb"] + '_' + str(counter[v["verb"]])
                
    def get_lemma(word,is_verb):
        return lemmatizer.lemmatize(word.lower(), wn.VERB if is_verb else wn.NOUN)
    

    def load_model(self,model_name):
        if model_name == 'ner':
            self.ner_spacy = spacy.load('en_core_web_lg',disable=['parser', 'tagger']) 
        if model_name == 'pos':
            self.pos_tagger = spacy.load("en_core_web_lg",disable=['ner', 'parser'])
        if model_name == 'parse':
            self.parser = spacy.load("en_core_web_lg",disable=['ner'])
        if model_name == 'dep':
            self.dep_tagger = spacy.load("en_core_web_lg",disable=['ner'])
        if model_name == 'sentencizer':
            self.nlp = English()
            #self.nlp.add_pipe(self.nlp.create_pipe('sentencizer')) 
            self.nlp.add_pipe('sentencizer') 
   
    
    def seperate_sentences(self,text):
        doc = self.nlp(text)
        #sentences = [sent.string.strip() for sent in doc.sents]
        sentences = [sent.text.strip() for sent in doc.sents]
        return sentences
    

    def cos_sim(x,y):
        a = np.array(x)
        b = np.array(y)
        if norm(a) == 0 or norm(b) == 0 :
            return 0
        return abs(dot(a, b)/(norm(a)*norm(b)))

    
    def extract_VO_from_docs_lambda(self,doc_srl,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT']):
        out = {}
        exclude = []
        for doc in doc_srl:
            out[doc] = []
            for sent in doc_srl[doc]:
                

                for v in doc_srl[doc][sent]:
                    if 'V' in doc_srl[doc][sent][v] :
                        
                        cont = True
                        for arg in arg_constrain:
                            if arg=='forbid':
                                 for srl_arg in  doc_srl[doc][sent][v]:
                                     if srl_arg in arg_constrain[arg]:
                                         cont = False 
                                         break
                                 if cont == False :
                                     break
                            elif arg not in doc_srl[doc][sent][v] :
                                cont = False 
                                break
                            elif arg_constrain[arg](doc_srl[doc][sent][v][arg]) == False:
                                cont = False 
                                break
                        if cont:
                            args = [doc_srl[doc][sent][v][arg]['text'] for arg in doc_srl[doc][sent][v] if arg in return_args]
                            VO = ' '.join(args) if join_args else args
                            out[doc].append((VO,sent))
        return out
    
    def filter_srl_docs_lambda(self,doc_srl,arg_constrain = {},return_args = None):
        out = {}
        for doc in doc_srl:
            out[doc] = {}
            for sent in doc_srl[doc]:
                out[doc][sent] = {}
                for v in doc_srl[doc][sent]:
                        
                        cont = True
                        for arg in arg_constrain:
                            if arg=='forbid':
                                 for srl_arg in  doc_srl[doc][sent][v]:
                                     if srl_arg in arg_constrain[arg]:
                                         cont = False 
                                         break
                                 if cont == False :
                                     break
                            elif arg not in doc_srl[doc][sent][v] :
                                cont = False 
                                break
                            elif arg_constrain[arg](doc_srl[doc][sent][v][arg]['text']) == False:
                                cont = False 
                                break
                        if cont:
                            out[doc][sent][v] = {i:doc_srl[doc][sent][v][i] for i in  doc_srl[doc][sent][v] if return_args == None or i in return_args }
        return out
    
    def extract_VO_from_sents_lambda(self,sents_srl,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT']):
        out = {}
        exclude = []

        for sent in sents_srl:
            out[sent] = []

            for v in sents_srl[sent]:
                if 'V' in sents_srl[sent][v] :
                    
                    cont = True
                    for arg in arg_constrain:
                        if arg=='forbid':
                             for srl_arg in  sents_srl[sent][v]:
                                 if srl_arg in arg_constrain[arg]:
                                     cont = False 
                                     break
                             if cont == False :
                                 break
                        elif arg not in sents_srl[sent][v] :
                            cont = False 
                            break
                        elif arg_constrain[arg](sents_srl[sent][v][arg]['text']) == False:
                            cont = False 
                            break
                    if cont:
                        args = [sents_srl[sent][v][arg]['text'] for arg in sents_srl[sent][v] if arg in return_args]
                        VO = ' '.join(args) if join_args else args
                        out[sent].append((VO,sent))
        return out
    
    def extract_VO_from_sents(self,sents_srl,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT']):
        out = {}
        for sent in sents_srl:
            out[sent] = []

                
            for v in sents_srl[sent]:
                if 'V' in sents_srl[sent][v] :
                    
                    cont = True
                    for arg in arg_constrain:
                        if arg=='forbid':
                             for srl_arg in  sents_srl[sent][v]:
                                 if srl_arg in arg_constrain[arg]:
                                     cont = False 
                                     break
                             if cont == False :
                                 break
                        elif arg not in sents_srl[sent][v] :
                            cont = False 
                            break
                        elif arg_constrain[arg](sents_srl[sent][v][arg]['text']) == False:
                            cont = False 
                            break
                    if cont:
                        args = [sents_srl[sent][v][arg]['text'] for arg in sents_srl[sent][v] if arg in return_args]
                        VO = ' '.join(args) if join_args else args
                        out[sent].append((VO,sent))
        return out
    def extract_VO_from_srl(srl,sent,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT']):
        exclude = []

        VO = ''
        # for v in srl:
        if 'V' in srl and srl['V']['text'] not in exclude:
            
            cont = True
            for arg in arg_constrain:
                if arg not in srl:
                    cont = False 
                    break
                elif srl[arg]['text'].lower() not in arg_constrain[arg] and arg_constrain[arg] != 'any':
                    cont = False 
                    break
            if cont:
                args = [srl[arg]['text'] for arg in srl if arg in return_args]
                VO = ' '.join(args) if join_args else args
        return VO
