#!python -m pip install textblob
import matplotlib.pyplot as plt
import numpy as np
import pickle
import math
import nltk
#!pip3 install sklearn
#from sklearn import preprocessing


#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#text = nltk.word_tokenize("They refuse to permit us to obtain the refuse permit")
#pos_tagged = nltk.pos_tag(text)

#nouns = filter(lambda x:x[1]=='NN',pos_tagged)

from statistics import mode,mean

#doc_id='77cd57f12232460986766ddda35b4b07' #8.png
#doc_id='a33f104af2574befbecfcd257ca6d2fc' #10.png
#doc_id='1d6aa3f73e354354ade7418991b5e715'  #2.png
#doc_id = 'c8e9b14bea8c438c8fbc983ac22b7600' #4.jpg
#doc_id = 'ae620e6ac5a14a95998d2fdd60ce1c76' #20.pdf
#doc_id = '918ebbccbe144428a7089ffa9d550c96' #1.png
#doc_id='72b74feba3c2456cafd64a53f0e93b35'    #3.png
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
doc_id='111e7ecada8c4cac9455603448ef96c1'     #13.png

with open('tmp/local_storage/{}.dm'.format(doc_id), 'rb') as mf:
    doc = pickle.load(mf)
page = doc.pages[0]


print("------------------------------------------------------------------------------------------------------------")

b_h_loc=[]
i=0
confidence_score=[]
case=[]
size=[]
b_w_amount=[]
block_empt=[]
block_center2=[]
Texts=[]
prev_bot=0
b_margin=[]
symbol_w=[]
tags=[]
spec_symbols=[]
p_Left,p_Top,p_Right,p_Bottom=page.bbox[0],page.bbox[1],page.bbox[2],page.bbox[3]
#print(p_Left,p_Top,p_Right,p_Bottom)
b_Bottom=p_Top
results=[]
for block in page.blocks:
    w_width=[]
    count=0
    lines_height=0
    uc_words = 0
    t_words = 0
    
    #print(block_center2)
    #print()
    
    block_words = " ".join([word.value for line in block.lines for word in line.words])
    text = nltk.word_tokenize(block_words)
    pos_tagged = nltk.pos_tag(text)

    nouns=list(filter(lambda x:x[1] in ('NN','NNS','NNP','NNPS'),pos_tagged))
    #print(nouns)
    verbs=list(filter(lambda x:x[1] in ('VB','VBD','VBZ','VBG','VBP','VBN','MD'),pos_tagged))
    #print(verbs)
    digits=list(filter(lambda x:x[1]=='CD',pos_tagged))
    #print(digits)
    if(len(nouns)>0):
        count=count+1
    
    if(len(verbs)>1):
        count=count-1
        
    if(len(digits)>0):
        count=count-1
    if any([True for x in ['link:','http:','https:','www.','.com','.html'] if x in block_words]):
        count=count-1
        
    if count<1:
        if len(digits)>1:
            tags.append(-0.5)
        else:
            tags.append(0)
    else:
        tags.append(1)
    
    Texts.append(block_words)
    #print(block_words)
    b_w_amount.append(len(block_words.split()))

   

    
      
    lines_height=[]
    v=0
    l_margin=[]
    prev_bot=0
    for line in block.lines:
        Left,Top,Right,Bottom=line.bbox[0],line.bbox[1],line.bbox[2],line.bbox[3]
        lines_height.append(Bottom-Top)
        line_words = " ".join([word.value for word in line.words])
        if len(block.lines)<2:
            l_margin.append(Top-b_Bottom)
        else:    
            if v>0:
                l_margin.append(Top-prev_bot)
        prev_bot=Bottom    
       # print(line_words)
        for word in line.words:
            w_width.append(word.get_symbol_sizes()[0][0])
            if word.value.isupper():
                uc_words = uc_words + 1
            elif word.value.istitle():
                t_words = t_words + 1     
        v=v+1
    #print("MARs",l_margin)   
    #print("mean",mean(l_margin))
    
    b_margin.append(mean(l_margin))  
    
    b_Left,b_Top,b_Right,b_Bottom=block.bbox[0],block.bbox[1],block.bbox[2],block.bbox[3]
    block_empt.append((b_Left+(p_Right-b_Right))/2)
    block_center2.append(b_Left/(p_Right/2))
                
    symbol_w.append(mean(w_width))
    
    b_h_loc.append(b_Bottom/p_Bottom)
    
    if any([True for x in [';',',','//',':','<','>','*'] if x in block_words]) or block_words.endswith('.'):
        spec_symbols.append(0)
    else:
        spec_symbols.append(1)
    
                
    size.append(mean(lines_height))
        
    #if b_Left>p_Right/2:
    #    block_empt[i]=0
    #    block_center2[i]=0
    #print(block_empt)    
        
       
 
    upercent=uc_words/b_w_amount[i]
    tpercent=t_words/b_w_amount[i]
    #print("Upper and Title case percents: ",upercent,tpercent)
    #print(tpercent)
    case.append(tpercent+upercent)
    i=i+1
   # print("Amount of blocks",len(page.blocks))
print(size)
print(mean(size))
#print(b_margin)
max_bw=max(symbol_w)
#b_margin.append(p_Bottom-b_Bottom)
#print("MARGINS: ",b_margin)

b_w_amount=([1-x/mean(b_w_amount) if x<mean(b_w_amount) else 0 for x in b_w_amount])

b_h_loc=([1-(x-min(b_h_loc))/(max(b_h_loc)-min(b_h_loc)) for x in b_h_loc])
aver_size=mode(size)

size=[(x-min(size))/(max(size)-min(size)) for x in size]    
symbol_w=[(x-min(symbol_w))/(max(symbol_w)-min(symbol_w)) for x in symbol_w]

block_empt=[(x-min(block_empt))/(max(block_empt)-min(block_empt)) for x in block_empt]
block_center2=[(x-min(block_center2))/(max(block_center2)-min(block_center2)) for x in block_center2]
center_empt=[(x+y)/2 for x,y in zip(block_empt,block_center2)]
center_empt=[(x-min(center_empt))/(max(center_empt)-min(center_empt)) for x in center_empt]

case=[x if x>=0.5 else 0 for x in case]
if any([True for x in case if x > 0.5]):
    case=[(x-min(case))/(max(case)-min(case)) for x in case]
else:
    case=[0]*len(case)

Features=[x*0.39+a*0.53+y*0.3+c*0.29+b*0.35 for x,a,y,c,b in 
          zip(size,symbol_w,block_empt,case,b_w_amount)]
b_h_loc=[x if y>0.75 else 0  for x,y in zip(b_h_loc,Features)]
Features=[x+y*0.25 for x,y in zip(Features,b_h_loc)]
#Features=[x*0.8+(z*y)*0.3+c*0.1+b*0.2 for x,y,z,c,b in zip(size,block_height_loc,block_center,case,b_w_amount)]
Final=dict(zip(Features,Texts))
m=max(Final)

f_threshold=[1 if x >1 else 0 for x in Features]
aver_size=[1 if x > mean(size) else 0 for x in size]
print("Spec   ",spec_symbols)
print("Tags   ",tags)
print("Thresh ",f_threshold)
print("Aver_s ",aver_size)
confidence_score=[(x+y+z+a)/4 for x,y,z,a in zip(spec_symbols,tags,f_threshold,aver_size)]

#norm_Features=[(x/max(Features))for x in Features]
norm_Features=[(x-min(Features))/(max(Features)-min(Features)) if y >0.49 
               else (x-min(Features))/(max(Features)-min(Features))*0.1 
               for x,y in zip(Features,confidence_score)]
norm_Final=dict(zip(norm_Features,Texts))

if any([True for x in norm_Features if x>0.5]):
    print("Headings Found:",len([x for x in norm_Features if x>0.5]))
    
    print("{:.2f}% MAIN HEADING - {}".format(max(norm_Final),norm_Final[max(norm_Final)]))
    print("------------------------------------------------------------------------------------------------------")
    for key in norm_Final:
        if key < max(norm_Final) and key > 0.35:
            print("{:.2f}% SUB HEADINGS - {}".format(key,norm_Final[key]))
    print("------------------------------------------------------------------------------------------------------")        

else:
    print("Headings Not Found")
#print(norm_Features)   
#print(norm_Final)
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
plt.plot(np.arange(0,len(page.blocks)),size,label="size")
plt.plot(np.arange(0,len(page.blocks)),symbol_w,label="width")
plt.legend()
plt.figure()
plt.ylabel("Center and empty")
plt.xlabel("Block")
plt.plot(np.arange(0,len(page.blocks)),center_empt,label="center_empt")
plt.plot(np.arange(0,len(page.blocks)),block_empt,label="empty")
plt.plot(np.arange(0,len(page.blocks)),block_center2,label="center2") 
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
plt.plot(np.arange(0,len(page.blocks)),[1] * len(page.blocks) )
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.ylim(0, 1.01)
plt.plot(np.arange(0,len(page.blocks)),confidence_score,label="Confidence_score")
plt.plot(np.arange(0,len(page.blocks)),[0.49] * len(page.blocks) )
plt.legend()
plt.figure()
plt.ylabel("norm_Features")
plt.xlabel("Block")  
#plt.ylim(0, 1.01)
plt.plot(np.arange(0,len(page.blocks)),norm_Features,label="norm_Final")
#plt.plot(np.arange(0,len(page.blocks)),[0.5] * len(page.blocks) )
plt.legend()
plt.show()      
