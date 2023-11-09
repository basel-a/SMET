# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 16:24:28 2023

@author: basel
"""



from sentence_transformers import SentenceTransformer
import pickle
from scipy.special import softmax
from parse_class import Parser
from nlp_general import NLP
# import pandas as pd
import funs
nlp = NLP()
nlp.load_model('dep')
nlp.load_model('sentencizer')

LR_model = pickle.load(open("LR_ATT&CK_model_V2.pkl", 'rb'))
emb_model = SentenceTransformer("basel/ATTACK-BERT")
id2mitre = funs.read_json_as_dict('id2mitre.json')
id2label = funs.read_json_as_dict('id2ATT&CK_V2.json')
id2label = {int(i):id2label[i] for i in id2label}

def get_verbs_tag(srl):
    verbs_tag= {}

    for v in srl['verbs']:

        try:
            v_ind = v['tags'].index("B-V")
        except:

            continue
        for other_v in srl['verbs']:
            if other_v['tags'][v_ind] not in ('B-V','O'):
                
                try:
                    other_v_ind = other_v['tags'].index("B-V")
                except:

                    continue

                if v['id'] not in verbs_tag:
                    verbs_tag[v['id']] = [(other_v["verb"] , "-".join(other_v['tags'][v_ind].split("-")[1:]),abs(v_ind - other_v_ind),other_v_ind)]
                else:
                    verbs_tag[v['id']] += [(other_v["verb"] , "-".join(other_v['tags'][v_ind].split("-")[1:]),abs(v_ind - other_v_ind),other_v_ind)]
    
    for i in verbs_tag:
        verbs_tag[i] = sorted(verbs_tag[i],key = lambda x:x[2])
    return verbs_tag
    
def add_arg0_from_parent(srl,srl_dict):

    verbs_tag = get_verbs_tag(srl)
    for v in srl_dict:
        if 'V' in srl_dict[v] and srl_dict[v]['V']['text'] in verbs_tag and 'ARG0' not in srl_dict[v]  and v in verbs_tag:
            parent_verb = verbs_tag[v][0][0]
            if parent_verb in srl_dict and  'ARG0' in srl_dict[parent_verb]:
                srl_dict[v]['ARG0'] = srl_dict[parent_verb]['ARG0'].copy()
                
                
def get_AVs(text,CVE = False):
    
    sents = nlp.seperate_sentences(text)
    cve_srl = {}
    for sent in  sents:
        try:
            srl = Parser.extract_srl(sent)
            Parser.add_v_id_srl(srl)
            srl_dict = Parser.srl_to_dict(srl)
            add_arg0_from_parent(srl,srl_dict)
            cve_srl[sent] = (srl_dict)
        except:
            print('error')
   
    if CVE:
        arg_constrain = {'ARG0' : lambda x : 'attacker' in x.lower() or 'adversary' in x.lower() or 'user' in  x.lower() or 'vulnerability' in x }
        vo0 = nlp.extract_VO_from_sents_lambda(cve_srl,arg_constrain)
        
        arg_constrain = {'ARG1' : lambda x : 'attacker' in x.lower() or 'adversary' in x.lower() or 'user' in  x or 'vulnerability' in x.lower() }
        vo1 = nlp.extract_VO_from_sents_lambda(cve_srl,arg_constrain)
        
        arg_constrain = {'V' : lambda x : 'allow' in x.lower() or 'lead' in x.lower()  or 'result' in x.lower()}
        vo2 = nlp.extract_VO_from_sents_lambda(cve_srl,arg_constrain) #or 'caus' in x.lower() 
        
        cve_vos_filtered = { key:vo0.get(key,[])+vo1.get(key,[])+vo2.get(key,[]) for key in set(list(vo0.keys())+list(vo1.keys())+list(vo2.keys())) }
        cve_vos = set([i[0] for j in cve_vos_filtered.values() for i in j ])
        cve_vos.add(text)

        
    else:
        arg_constrain = {}
        vo = nlp.extract_VO_from_sents_lambda(cve_srl,arg_constrain)
        cve_vos = set([i[0] for j in vo.values() for i in j ])
    return cve_vos      
        

def predict_techniques(emb,clf,id2label):
    dec = clf.decision_function([emb])
    out = softmax(dec)[0]
    return sorted(list( zip([id2mitre[id2label[i]] for i in  range(len(dec[0])) ],  out)), key = lambda x:x[1], reverse=True)


def predict_per_vo(cve_vos, rank,id2mitre):

    out = []
    for vo in cve_vos:
        if vo.strip() == '':
            continue 
        vo = vo
        dec = rank(vo)
        out.append([(j[0],j[1]) for j in dec])

        
    outa =  [j for k in out for j in k]
    outa = sorted(outa,key = lambda x:x[1],reverse = True )
    abc = []
    cdf = []
    for k in outa:
        if k[0] not in cdf:
            abc.append(k)
            cdf.append(k[0])
    outa = [i for i in abc if i[0]]
    
    return outa

#map text to ATT&CK
def map_text(text,CVE = False):
    rank = lambda x:predict_techniques(emb_model.encode(x),LR_model,id2label)
    vos = get_AVs(text,CVE = CVE)
    return predict_per_vo(vos,rank,id2mitre)

#map attack vector to ATT&CK
def map_attack_vector(AV):
    return predict_techniques(emb_model.encode(AV),LR_model,id2label)


