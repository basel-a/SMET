# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 04:03:07 2023

@author: basel
"""

from SMET import map_text,map_attack_vector

#map attack vectors to ATT&CK
AV1 = 'take screenshot'
mapping1 = map_attack_vector(AV1)

AV2 = 'delete logs'
mapping2 = map_attack_vector(AV2)

AV3 = 'exfiltrate data to C2 server'
mapping3 = map_attack_vector(AV3)



#map CVE to ATT&CK
cve = ""
mapping = map_text(cve,CVE = True)


#map any text to ATT&CK
cve = ""
mapping = map_text(cve,CVE = False)


#get embedding using ATT&CK 
from sentence_transformers import SentenceTransformer

text = ""
emb_model = SentenceTransformer("basel/ATTACK-BERT")
embedding = emb_model.encode(text)



