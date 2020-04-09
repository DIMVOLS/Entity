#!python -m pip install textblob
import matplotlib.pyplot as plt
import numpy as np
import pickle
import math
import nltk

from statistics import mode,mean

#doc_id='77cd57f12232460986766ddda35b4b07' #8.png
#doc_id='a33f104af2574befbecfcd257ca6d2fc' #10.png
#doc_id='1d6aa3f73e354354ade7418991b5e715'  #2.png
#doc_id = 'c8e9b14bea8c438c8fbc983ac22b7600' #4.jpg
#doc_id = 'ae620e6ac5a14a95998d2fdd60ce1c76' #20.pdf
#doc_id = '918ebbccbe144428a7089ffa9d550c96' #1.png
doc_id='72b74feba3c2456cafd64a53f0e93b35'    #3.png
#doc_id='8d9d7979471e49439f4065ce35722d52'    #5.png
#doc_id='edbe20b8959e4f1bb0e68b4cb4a52c5b'    #25.pdf
#doc_id='f5d11cf0148e45c3b6b2b40266ac179d'     #16.pdf
#doc_id='3f8ae2df94824b3382305e9474ab40b1'      #10.pdf
#doc_id='1840379e455a4d09899d0ff69235effe'    #10-1.pdf
#doc_id='6773c526e29e402c8077331a7ae59348'    #10-2.pdf
#doc_id='7cf28796e51a491397ad7886e3c96b78'     #10-3.pdf
#doc_id='e9c24931ffa84a7d801851eb433a3779'    #10-4.pdf
#doc_id='a89140e96b134499b8a9dee111cda140'    #10-5.pdf
#doc_id='1f55083d0a204bcdbfb8e4ee924dc2c1'    #10-6.pdf
#doc_id='ede60de83ace44208c3b89df3ef22698'    #10-7.pdf
#doc_id='5b47cabd04d9471cb86fc5d7a71c2133'    #10-8.pdf
#doc_id='6a9c0fc4b8ea475b8be93736600bffa9'    #10-9.pdf
#doc_id='9375e0e91a7c43bfb5b0b1164b8ec3f4'     #11.png
#doc_id='2afbf98005394bc1a5701a11d8935fb6'     #12-1.png
#doc_id='111e7ecada8c4cac9455603448ef96c1'     #13.png

with open('tmp/local_storage/{}.dm'.format(doc_id), 'rb') as mf:
    doc = pickle.load(mf)
page = doc.pages[0]


print("------------------------------------------------------------------------------------------------------------")


class Features:
    def __init__(self):
        for line in block.lines:
            self.line_words = " ".join([word.value for word in line.words])
            self.block_words2 = " ".join([word.value for line in block.lines for word in line.words])  
        
class size1(Features):
    def get_size(self):
        lines_height=[]
        s_width=[]
        for line in block.lines:
            l_Left=line.bbox[0]
            l_Top=line.bbox[1]
            l_Right=line.bbox[2]
            l_Bottom=line.bbox[3]
            lines_height.append(l_Bottom-l_Top) 
            for word in line.words:
                s_width.append(word.get_symbol_sizes()[0][0])
        return mean(lines_height),mean(s_width)
    
class case1(Features):
    def get_case(self):
        uc_words1=0
        t_words1=0
        for line in block.lines:
            for word in line.words:
                # different weights for types
                if word.value.isupper():
                    uc_words1 = uc_words1 + 1
                elif word.value.istitle():
                    t_words1 = t_words1 + 1     
        return (t_words1 +uc_words1)/len(self.block_words2.split())
    
    
class words_amount1(Features):
    def get_words_amount(self):
        block_w_amount=(len(self.block_words2.split()))       
        return block_w_amount  
    
    
class top_location1(Features):
    def get_top_location(self):
        top_location = b_Bottom/p_Bottom       
        return top_location    

    
class block_empt1(Features):
    def get_block_empt(self):
        block_empt=(b_Left+(p_Right-b_Right))/2     
        return block_empt  
    
    
class tags1(Features):
    def check_tags(self):
        count=0
        pos_tagged = nltk.pos_tag(nltk.word_tokenize(self.block_words2))

        nouns=list(filter(lambda x:x[1] in ('NN','NNS','NNP','NNPS'),pos_tagged))
        verbs=list(filter(lambda x:x[1] in ('VB','VBD','VBZ','VBG','VBP','VBN','MD'),pos_tagged))
        digits=list(filter(lambda x:x[1]=='CD',pos_tagged))

        if len(digits)>0 or len(verbs)>1 or len(nouns)<1:
            tag=0
        else:
            if any([True for x in ['link:','http:','https:','www.','.com','.html'] if x in self.block_words2]):
                tag = 0
            else:
                tag = 1
        
        return tag    

    
class spec_symbols1(Features):
    def check_spec_symbols(self):
        if any([True for x in [';',',','//',':',
                               '<','>','*'] if x in self.block_words2]) or self.block_words2.endswith('.'):
            spec_symbols=0
        else:
            spec_symbols=1
        print(self.block_words2,spec_symbols)    
        return spec_symbols   

    
class lines_amount1(Features):
    def get_lines_amount(self):
        lines_amount=(b_Bottom-b_Top)/lines_height[i]
        
        return lines_amount
    
class block_center1(Features):
    def get_block_center(self):
        block_center=min(b_Left,(p_Right-b_Right))
        return block_center
    
i=0    
b_h_loc=[]
confidence_score=[]
case=[]
l_height=[]
b_w_amount=[]
block_empt=[]
block_center=[]
Texts=[]
tags=[]
lines_amount=[]
spec_symbols=[]
p_Left,p_Top,p_Right,p_Bottom=page.bbox[0],page.bbox[1],page.bbox[2],page.bbox[3]
b_Bottom=p_Top
results=[]


for block in page.blocks:
    b_Left,b_Top,b_Right,b_Bottom=block.bbox[0],block.bbox[1],block.bbox[2],block.bbox[3]  
        
    f1 = size1()
    f2 = case1() 
    f3 = words_amount1()
    f4 = top_location1()
    f5 = block_empt1()
    f6 = tags1()
    f7 = spec_symbols1()
    f8 = lines_amount1()
    f9 = block_center1()

    
    l_height.append(f1.get_size()[0])
    symbol_w.append(f1.get_size()[1])
    case.append(f2.get_case())
    b_w_amount.append(f3.get_words_amount())
    b_h_loc.append(t4.get_top_location())
    block_empt.append(f5.get_block_empt())
    tags.append(f6.check_tags())
    spec_symbols.append(f7.check_spec_symbols())
    lines_amount.append(f8.get_lines_amount())
    block_center.append(f9.get_block_center())  
    
    Texts.append(" ".join([word.value for line in block.lines for word in line.words])) 

# Normalize features from 0 to 1

b_w_amount=([1-x/mean(b_w_amount) if x<mean(b_w_amount) else 0 for x in b_w_amount])

b_h_loc=([1-(x-min(b_h_loc))/(max(b_h_loc)-min(b_h_loc)) for x in b_h_loc])

l_height=[(x-min(l_height))/(max(l_height)-min(l_height)) for x in l_height] 

symbol_w=[(x-min(symbol_w))/(max(symbol_w)-min(symbol_w)) for x in symbol_w]

block_empt=[(x-min(block_empt))/(max(block_empt)-min(block_empt)) for x in block_empt]

block_center=[(x-min(block_center))/(max(block_center)-min(block_center)) for x in block_center]

case=[x if x>=0.5 else 0 for x in case]

if any([True for x in case if x > 0.5]):
    case=[(x-min(case))/(max(case)-min(case)) for x in case]
else:
    case=[0]*len(case)

Features=[x*0.4+a*0.52+y*0.25+c*0.27+z*0.29 for x,a,y,c,z in 
          zip(l_height,symbol_w,block_empt,case,b_w_amount)]

# add top_location if current features higher than threshold
b_h_loc=[x if y>0.75 else 0  for x,y in zip(b_h_loc,Features)]
Features=[x+y*0.25 for x,y in zip(Features,b_h_loc)]
Final=dict(zip(Features,Texts))


case=[x if x>=0.5 else 0 for x in case]  
f_threshold=[1 if x >0.8 else 0 for x in Features]
aver_size=[1 if x > mean(l_height) else 0 for x in l_height]
aver_lines=[1 if x < mean(lines_amount)/2 else 0 for x in lines_amount]
aver_center=[x if x > mean(block_center) else 0 for x in block_center]

print("Spec   ",spec_symbols)
print("Tags   ",tags)
print("Thresh ",f_threshold)
print("Aver_s ",aver_size)
print("Aver_l ",aver_lines)
print("Aver_c ",aver_center)

confidence_score=[(x+y+z+a+b+c)/6 for x,y,z,a,b,c in zip(spec_symbols,tags,f_threshold,aver_size,aver_lines,aver_center)]


norm_Features=[(x-min(Features))/(max(Features)-min(Features)) if y >=0.65 
               else (x-min(Features))/(max(Features)-min(Features))*0.1 
               for x,y in zip(Features,confidence_score)]

# Final Dictionary
norm_Final=dict(zip(norm_Features,Texts))

if any([True for x in norm_Features if x>0.4]):
    print("Headings Found:",len([x for x in norm_Features if x>0.4]))
    
    print("{:.2f}% MAIN HEADING - {}".format(max(norm_Final),norm_Final[max(norm_Final)]))
    print("------------------------------------------------------------------------------------------------------")
    for key in norm_Final:
        if key < max(norm_Final) and key > 0.4:
            print("{:.2f}% SUB HEADINGS - {}".format(key,norm_Final[key]))
    print("------------------------------------------------------------------------------------------------------")        

else:
    print("Headings Not Found")

i=0

for key in norm_Final:
    print("#{} - {:.2f}, {}".format(i,key,norm_Final[key]))
    if key>0.5:
        results.append(i)
    i=i+1  
    
#with open('/home/dim/results.txt', 'a') as the_file:
#    the_file.write(doc_id+'\n'+str(results)+'\n')
print(results)   

plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block") 
plt.plot(np.arange(0,len(page.blocks)),aver_lines,label="aver_lines")
plt.legend()
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")      
plt.plot(np.arange(0,len(page.blocks)),l_height,label="l_height")
plt.plot(np.arange(0,len(page.blocks)),symbol_w,label="width")
plt.legend()
plt.figure()
plt.ylabel("Center and empty")
plt.xlabel("Block")
plt.plot(np.arange(0,len(page.blocks)),aver_center,label="aver_center")
plt.plot(np.arange(0,len(page.blocks)),block_empt,label="empty")
plt.legend()
plt.figure()
plt.ylabel("Center and h_location")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),b_h_loc,label="height_location")
plt.legend()
plt.figure()
plt.ylabel("Case")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),case,label="case")
plt.legend()
plt.ylabel("Words_amount_percent")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),b_w_amount,label="b_w_amount")
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),tags,label="tags")
plt.plot(np.arange(0,len(page.blocks)),spec_symbols,label="spec_symbols")
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.ylim(0, 2)
plt.plot(np.arange(0,len(page.blocks)),Features,label="Final")
plt.plot(np.arange(0,len(page.blocks)),[0.8] * len(page.blocks) )
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.ylim(0, 1.01)
plt.plot(np.arange(0,len(page.blocks)),confidence_score,label="Confidence_score")
plt.plot(np.arange(0,len(page.blocks)),[0.65] * len(page.blocks) )
plt.legend()
plt.figure()
plt.ylabel("norm_Features")
plt.xlabel("Block")  
#plt.ylim(0, 1.01)
plt.plot(np.arange(0,len(page.blocks)),norm_Features,label="norm_Final")
plt.plot(np.arange(0,len(page.blocks)),[0.4] * len(page.blocks) )
plt.legend()
plt.show()      
