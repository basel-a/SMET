# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 04:03:07 2023

@author: basel
"""

from SMET import map_text,map_attack_vector

#Mapping tips:
#When the input is short (e.g., one sentence or attack action) use map_attack_vector()
#For inputs that consist of a few lines, such as a CVE entry of a paragraph from a CTI report use map_text() 
#In cases where the input is long, like a full CTI report, segmented the text into multiple paragraphs or sentences and processed each separately


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


######
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('basel/ATTACK-BERT')

sentences = ["the account has weak password", "attacker gain an initial access to the machine"]

embeddings = model.encode(sentences)

from sklearn.metrics.pairwise import cosine_similarity
print(cosine_similarity([embeddings[0]], [embeddings[1]]))





