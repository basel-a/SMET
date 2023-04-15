# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 23:21:08 2020

@author: babdeen
"""


# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 23:01:55 2020

@author: babdeen
"""

from allennlp.predictors.predictor import Predictor
from nlp_general import NLP
# import allennlp_models.syntax.srl
# SRL = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.11.19.tar.gz")
SRL = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")
# DT = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")
# CT = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/elmo-constituency-parser-2020.02.10.tar.gz")


class Parser:
    def extract_srl(text):
        srl = SRL.predict(text)
        Parser.add_v_id_srl(srl)
        # srl_dict = Parser.srl_to_dict(srl)
        return srl
    
    # def extract_dt(text):
    #     return DT.predict(text)
    # def extract_ct(text):
    #     return CT.predict(text)
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
                        # if newTag == 'V':
                        SRLDict[verb_str][newTag]['index'] = ind
                    else :   
                        newTag = tag[tag.find('-')+1:]
                        if newTag not in SRLDict[verb_str]:
                            continue
                        SRLDict[verb_str][newTag]['text'] += (' ' + srl['words'][ind]) 
    
        return SRLDict
    
    
    def srl_to_dict_from_dict(srls):
        return {srl:Parser.srl_to_dict(srls[srl]) for srl in srls}
    
    def srl_to_dict_from_list(srls):
        return [Parser.srl_to_dict(srls[srl]) for srl in srls]
    
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
    
    def add_v_id_srl_from_dict(srls):
        for srl in srls:
            Parser.add_v_id_srl(srls[srl])
            
            
    def get_words_verb(sent,is_SRL = True,args = ['ARG0','ARG1','ARG2','ARG3'], ):
        words_verbs = {}
        if is_SRL:
            srl = sent
        else:
            srl = Parser.extract_srl(sent)
            srl = Parser.srl_to_dict(srl)
            
        for v in srl:
            if 'V' not in srl[v]:
                continue 
            args_join = ' '.join([srl[v][arg]['text'] if arg in srl[v] else '' for arg in args])
            for w in args_join.split():
                if w in words_verbs:
                    words_verbs[w].append(srl[v]['V']['text'])
                else:
                    words_verbs[w] = [srl[v]['V']['text']]
        return words_verbs
    
    def get_words_sub(sent, is_SRL = True, args = ['ARG1','ARG2','ARG3']):
        words_subs = {}
        
        if is_SRL:
            srl = sent
        else:
            srl = Parser.extract_srl(sent)
            srl = Parser.srl_to_dict(srl)
            
        for v in srl:
            if 'ARG0' in srl[v]:
                args_join = ' '.join([srl[v][arg]['text'] if arg in srl[v] else '' for arg in args])
    
                for w in args_join.split():
                    if w in words_subs:
                        words_subs[w].append(srl[v]['ARG0']['text'])
                    else:
                        words_subs[w] = [srl[v]['ARG0']['text']]  
        return words_subs
    
    def extract_VO_from_docs(doc_srl,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT'], exclude_dep = ['amod']):
        out = []
        for doc in doc_srl:
            for sent in doc_srl[doc]:
                
                if exclude_dep != []:
                    exclude = NLP.extract_dep(sent, exclude_dep)
                for v in doc_srl[doc][sent]:
                    if 'V' in doc_srl[doc][sent][v]  and doc_srl[doc][sent][v]['V']['text'] not in exclude:
                        
                        cont = True
                        for arg in arg_constrain:
                            if arg not in doc_srl[doc][sent][v]:
                                cont = False 
                                break
                            elif doc_srl[doc][sent][v][arg]['text'].lower() not in arg_constrain[arg] and arg_constrain[arg] != 'any':
                                cont = False 
                                break
                        if cont:
                            args = [doc_srl[doc][sent][v][arg]['text'] for arg in doc_srl[doc][sent][v] if arg in return_args]
                            VO = ' '.join(args) if join_args else args
                            out.append((VO,sent))
        return out
    
    def extract_VO_from_sents(sents_srl,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT'], exclude_dep = ['amod']):
        out = []
        exclude = []
        for sent in sents_srl:
            
            if exclude_dep != []:
                exclude = NLP.extract_dep(sent, exclude_dep)
                
            for v in sents_srl[sent]:
                if 'V' in sents_srl[sent][v]  and sents_srl[sent][v]['V']['text'] not in exclude:
                    
                    cont = True
                    for arg in arg_constrain:
                        if arg not in sents_srl[sent][v]:
                            cont = False 
                            break
                        elif sents_srl[sent][v][arg]['text'].lower() not in arg_constrain[arg] and arg_constrain[arg] != 'any':
                            cont = False 
                            break
                    if cont:
                        args = [sents_srl[sent][v][arg]['text'] for arg in sents_srl[sent][v] if arg in return_args]
                        VO = ' '.join(args) if join_args else args
                        out.append((VO,sent))
        return out
    
    def extract_VO_from_srl(srl,sent,arg_constrain = {}, join_args = True, return_args = ['V','ARG1','ARG2','ARG3','ARGM-LOC','ARGM-EXT'], exclude_dep = ['amod']):

        if exclude_dep != []:
            exclude = NLP.extract_dep(sent, exclude_dep)
            
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
    
    
