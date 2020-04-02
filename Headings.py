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
doc_id='7cf28796e51a491397ad7886e3c96b78'     #10-3.pdf
#doc_id='e9c24931ffa84a7d801851eb433a3779'    #10-4.pdf
#doc_id='a89140e96b134499b8a9dee111cda140'    #10-5.pdf
#doc_id='1f55083d0a204bcdbfb8e4ee924dc2c1'    #10-6.pdf
#doc_id='ede60de83ace44208c3b89df3ef22698'    #10-7.pdf
#doc_id='5b47cabd04d9471cb86fc5d7a71c2133'    #10-8.pdf
#doc_id='6a9c0fc4b8ea475b8be93736600bffa9'    #10-9.pdf

with open('tmp/local_storage/{}.dm'.format(doc_id), 'rb') as mf:
    doc = pickle.load(mf)
page = doc.pages[0]

#print(page.blocks)
print("------------------------------------------------------------------------------------------------------------")
#print(page.bbox)
blockss=[]
b_h_loc=[]
i=0
up_cor=[]
case=[]
size=[]
size_case=[]
max_size=0
b_w_amount=[]
max_words=0
max_height=0
max_center=0
block_center=[]
Texts=[]
prev_bot=0
b_margin=[]
w_height=[]
symbol_w=[]
tags=[]
size2=[]
size3=[]
p_Left,p_Top,p_Right,p_Bottom=page.bbox[0],page.bbox[1],page.bbox[2],page.bbox[3]
#print(p_Left,p_Top,p_Right,p_Bottom)
for block in page.blocks:
   # print("BLOCK #",i)
    w_width=[]
    count=0
    lines_height=0
    uc_words = 0
    t_words = 0
    b_Left,b_Top,b_Right,b_Bottom=block.bbox[0],block.bbox[1],block.bbox[2],block.bbox[3]
   # print("COORDINATES",b_Left,b_Top,b_Right,b_Bottom)
    block_center.append((b_Left+(p_Right-b_Right))/2)
    #print("CENTER: ",block_center[i],b_Left,p_Right/2)
    
    block_words = " ".join([word.value for line in block.lines for word in line.words])
    text = nltk.word_tokenize(block_words)
    pos_tagged = nltk.pos_tag(text)
    #print(block_words) 
    #print(pos_tagged)
    nouns=list(filter(lambda x:x[1] in ('NN','NNS','NNP','NNPS'),pos_tagged))
    #print(nouns)
    verbs=list(filter(lambda x:x[1] in ('VB','VBD','VBZ','VBG','VBP','VBN','MD'),pos_tagged))
    #print(verbs)
    digits=list(filter(lambda x:x[1]=='CD',pos_tagged))
    #print(digits)
    if(len(nouns)>0):
        count=count+1
    
        #print("Nouns prob")
    if(len(verbs)>1):
        count=count-1
        #print("Verbs prob")
        
    if(len(digits)>0):
        count=count-1
        #print("Digits prob")
        
    if count<1:
        tags.append(0)
    else:
        tags.append(1)
    
    Texts.append(block_words)
    #print(block_words)
    b_w_amount.append(len(block_words.split()))
    #print(block_words,block_w_amount)
   # print("Words AMOUNT: ",block_w_amount)
    b_margin.append(b_Top-prev_bot)
    prev_bot=b_Bottom

    if len(block_words.split())>=max_words:
        max_words=len(block_words.split())    
        
    b_h_loc.append(b_Bottom/p_Bottom)
    #print("BLOCK_HEIGHT:",b_h_loc)
    if b_h_loc[i]>=max_height:
        max_height=b_h_loc[i]
        
    lines_height=[]    
    for line in block.lines:
        Left,Top,Right,Bottom=line.bbox[0],line.bbox[1],line.bbox[2],line.bbox[3]
        lines_height.append(Bottom-Top)
        for word in line.words:
            w_width.append(word.get_symbol_sizes()[0][0])
            w_height.append(word.get_symbol_sizes()[0][1])
            if word.value.isupper():
                uc_words = uc_words + 1
            elif word.value.istitle():
                t_words = t_words + 1 
        size3.append(max(w_height))        
    #print("WORDS SIZE",w_width)
    symbol_w.append(mean(w_width))
    size2.append(mean(size3))
    #print(size2)
    #print("SIZE:",i,lines_height)            
    size.append(mode(lines_height))
    if size[i]>=max_size:
        max_size=size[i]   
        
    if b_Left>p_Right/2:
        block_center[i]=0
        size[i]=0
        symbol_w[i]=0
        
    #print("Amount lines and size:",len(block.lines),size)
    upercent=uc_words/b_w_amount[i]
    tpercent=t_words/b_w_amount[i]
    #print("Upper and Title case percents: ",upercent,tpercent)
    #print(tpercent)
    case.append(tpercent+upercent)
    i=i+1
   # print("Amount of blocks",len(page.blocks))
max_bw=max(symbol_w)
b_margin.append(p_Bottom-b_Bottom)
#print("MARGINS: ",b_margin)

b_w_amount=([1-x/mean(b_w_amount) if x<mean(b_w_amount) else 0 for x in b_w_amount])

print(b_w_amount)

b_h_loc=([1-(x-min(b_h_loc))/(max(b_h_loc)-min(b_h_loc)) for x in b_h_loc])
aver_size=mode(size)
#print(tags)
#print(aver_size)
size2=[x for x in size2] 
size2=[(x-min(size2))/(max(size2)-min(size2)) for x in size2] 
size=[x/mean(size) for x in size] 
size=[(x-min(size))/(max(size)-min(size)) for x in size]    
symbol_w=[(x-min(symbol_w))/(max(symbol_w)-min(symbol_w)) for x in symbol_w]
#print("W",symbol_w)
#print("C",case)
#print(size)
block_center=[(x-min(block_center))/(max(block_center)-min(block_center)) for x in block_center]
case=[x if x>0.5 else 0 for x in case]
if any([True for x in case if x > 0.5]):
    case=[(x-min(case))/(max(case)-min(case)) for x in case]
else:
    case=[0]*len(case)
#case=[x if x>0.5 else 0 for x in case]
#print(case)
#w_case=[(y*z) for y,z in zip(case,b_w_amount)]
#print("size+case2: ",size_case)
Features=[x*0.4+a*0.5+z*0+y*0.25+c*0.25+b*0.25+v*0.12 for x,a,z,y,c,b,v in 
          zip(size,symbol_w,b_h_loc,block_center,case,b_w_amount,tags)]
b_h_loc=[x if y>0.7 else 0  for x,y in zip(b_h_loc,Features)]
Features=[x+y*0.3 for x,y in zip(Features,b_h_loc)]
#Features=[x*0.8+(z*y)*0.3+c*0.1+b*0.2 for x,y,z,c,b in zip(size,block_height_loc,block_center,case,b_w_amount)]
Final=dict(zip(Features,Texts))
m=max(Final)
if any([True for x in Features if x>1]):
    print("Headings Found")
else:
    print("Headings Not Found")
    
norm_Features=[(x/max(Features))for x in Features]
norm_Features2=[(x-min(Features))/(max(Features)-min(Features))for x in Features]
norm_Final=dict(zip(norm_Features,Texts))
print("MAIN HEADING - ",norm_Final[max(norm_Final)])
print("----------------------------------------------------------------------------------------------------------")
for key in norm_Final:
    if key < max(norm_Final) and key > 0.5:
        print("SUB HEADINGS - ",norm_Final[key])
print("----------------------------------------------------------------------------------------------------------")        
for key in norm_Final:
    print(key,norm_Final[key])       
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")      
plt.plot(np.arange(0,len(page.blocks)),size2,label="size2")
plt.legend()    
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")      
plt.plot(np.arange(0,len(page.blocks)),size,label="size")
plt.legend()
plt.figure()
plt.ylabel("Center")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),block_center,label="center")
plt.legend()
plt.ylabel("Height_location")
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
plt.ylabel("Symbols width")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),symbol_w,label="width")
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),tags,label="tags")
plt.legend()
plt.figure()
plt.ylabel("norm_Features")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),norm_Features,label="norm_Final")
plt.plot(np.arange(0,len(page.blocks)),[0.5] * len(page.blocks) )
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),Features,label="Final")
plt.plot(np.arange(0,len(page.blocks)),[0.5] * len(page.blocks) )
plt.legend()
plt.show()      
