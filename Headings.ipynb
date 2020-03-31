#!pip install matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pickle
import math

#doc_id = 'c8e9b14bea8c438c8fbc983ac22b7600' #4.jpg
#doc_id = 'ae620e6ac5a14a95998d2fdd60ce1c76' #20.pdf
#doc_id = '918ebbccbe144428a7089ffa9d550c96' #1.png
doc_id='72b74feba3c2456cafd64a53f0e93b35'    #3.png
#doc_id='8d9d7979471e49439f4065ce35722d52'    #5.png
#doc_id='edbe20b8959e4f1bb0e68b4cb4a52c5b'    #25.pdf
#doc_id='f5d11cf0148e45c3b6b2b40266ac179d'     #16.pdf
#doc_id='3f8ae2df94824b3382305e9474ab40b1'      #10.pdf

with open('tmp/local_storage/{}.dm'.format(doc_id), 'rb') as mf:
    doc = pickle.load(mf)
page = doc.pages[0]

#print(page.blocks)
print("------------------------------------------------------------------------------------------------------------")
#print(page.bbox)
blockss=[]
block_height_loc=[]
i=0
up_cor=[]
case=[]
size=[]
size_case=[]
max_size=0
block_words_amount=[]
max_words=0
max_height=0
max_center=0
block_center=[]
Final={}
Texts=[]

p_Left,p_Top,p_Right,p_Bottom=page.bbox[0],page.bbox[1],page.bbox[2],page.bbox[3]
#print(p_Left,p_Top,p_Right,p_Bottom)
for block in page.blocks:
   # print("BLOCK #",i)
    
    lines_height=0
    uc_words = 0
    t_words = 0
    b_Left,b_Top,b_Right,b_Bottom=block.bbox[0],block.bbox[1],block.bbox[2],block.bbox[3]
   # print("COORDINATES",b_Left,b_Top,b_Right,b_Bottom)
    block_center.append(b_Left/(p_Right/2))
    #print("CENTER: ",block_center[i],b_Left,p_Right/2)
    
    if b_Left>p_Right/2:
        block_center[i]=block_center[i]/5
    block_words = " ".join([word.value for line in block.lines for word in line.words])
    Texts.append(block_words)
    #print(block_words)
    block_words_amount.append(len(block_words.split()))
   # print("Words AMOUNT: ",block_words_amount)
    
    if len(block_words.split())>=max_words:
        max_words=len(block_words.split())    
        
    block_height_loc.append(b_Bottom/p_Bottom)
    #print("BLOCK_HEIGHT:",block_height_loc)
    if block_height_loc[i]>=max_height:
        max_height=block_height_loc[i]
        
    lines_height=[]    
    for line in block.lines:
        Left,Top,Right,Bottom=line.bbox[0],line.bbox[1],line.bbox[2],line.bbox[3]
        lines_height.append(Bottom-Top)
        for word in line.words:
            if word.value.isupper():
                uc_words = uc_words + 1
            elif word.value.istitle():
                t_words = t_words + 1         
    size.append(max(lines_height))
    if size[i]>=max_size:
        max_size=size[i]    
    #print("Amount lines and size:",len(block.lines),size)
    upercent=uc_words/block_words_amount[i]
    tpercent=t_words/block_words_amount[i]
    #print("Upper and Title case percents: ",upercent,tpercent)
    #print(tpercent)
    case.append(tpercent+upercent)
    i=i+1
   # print("Amount of blocks",len(page.blocks))
w_percent=([1-(x/max_words) for x in block_words_amount])
block_height_loc=([1-(x/max_height) for x in block_height_loc])
size=([x/max_size for x in size])    
#print("S",size)
#print("C",case)
#print("Words percent ",w_percent)
w_case=[(y*z) for y,z in zip(case,w_percent)]
size_case=([x+y for x,y in zip(size,w_case)])
#print("size+case2: ",size_case)
Features=[x*0.9+(z*c)*0.5+(y*b)*0.2 for x,y,z,c,b in zip(size,w_percent,block_height_loc,block_center,case)]
Final=dict(zip(Features,Texts))
print("MAIN HEADING - ",Final[max(Final)])
print("----------------------------------------------------------------------------------------------------------")
for key in Final:
    if key < max(Final) and key > 1:
        print("SUB HEADINGS - ",Final[key])
print("----------------------------------------------------------------------------------------------------------")        
for key in Final:
    print(key,Final[key])        
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")      
plt.plot(np.arange(0,len(page.blocks)),size,label="size")
plt.legend()
plt.figure()
plt.ylabel("Case")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),case,label="case")
plt.legend()
plt.figure()
plt.ylabel("Center")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),block_center,label="center")
plt.legend()
plt.figure()
plt.ylabel("Height_location")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),block_height_loc,label="height_location")
plt.legend()
plt.figure()
plt.ylabel("Words_amount_percent")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),w_percent,label="w_percent")
plt.legend()
plt.figure()
plt.ylabel("Features")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),[x*0.9+(z*c)*0.5+(y*b)*0.2 for x,y,z,c,b in zip(size,w_percent,block_height_loc,block_center,case)],label="Final")
plt.legend()
plt.show()      

