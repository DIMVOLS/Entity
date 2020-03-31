#!pip install matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pickle

#doc_id = 'c8e9b14bea8c438c8fbc983ac22b7600'
#doc_id = 'ae620e6ac5a14a95998d2fdd60ce1c76'
doc_id = '918ebbccbe144428a7089ffa9d550c96'

with open('tmp/local_storage/{}.dm'.format(doc_id), 'rb') as mf:
    doc = pickle.load(mf)
page = doc.pages[0]

#print(page.blocks)
print("------------------------------------------------------------------------------------------------------------")
print(page.bbox)
blockss=[]
i=0
up_cor=[]
case=[]
average_size=[]
size_case=[]
block_words_amount=[]
max=0
Left,Top,Right,Bottom=page.bbox[0],page.bbox[1],page.bbox[2],page.bbox[3]
for block in page.blocks:
    print("BLOCK #",i)
    i=i+1
    lines_height=0
    uc_words = 0
    t_words = 0
    b_Left,b_Top,b_Right,b_Bottom=block.bbox[0],block.bbox[1],block.bbox[2],block.bbox[3]
    print("COORDINATES",Left,Top,Right,Bottom)
    up_cor.append(b_Bottom)
    block_words = " ".join([word.value for line in block.lines for word in line.words])
    print(block_words)
    block_words_amount.append(len(block_words.split()))
    print("Words AMOUNT: ",block_words_amount)
    if len(block_words.split())>=max:
        max=len(block_words.split())
    block_weight=Bottom-Top
    for line in block.lines:
        Left,Top,Right,Bottom=line.bbox[0],line.bbox[1],line.bbox[2],line.bbox[3]
        line_height=Bottom-Top
        lines_height=lines_height+(Bottom-Top)
        for word in line.words:
            if word.value.isupper():
                uc_words = uc_words + 1
            elif word.value.istitle():
                t_words = t_words + 1
    average_size.append(lines_height/len(block.lines))
    print("Amount lines and average_height:",len(block.lines),lines_height/len(block.lines))
    upercent=uc_words/words_amount
    tpercent=t_words/words_amount
    print("Upper and Title case percents: ",upercent,tpercent)
    #print(tpercent)
    case.append(tpercent+upercent)
   # print("Amount of blocks",len(page.blocks))
w_percent=([1-(x/max) for x in block_words_amount])
    
print("S",average_size)
print("C",case)
print("Words percent ",w_percent)
size_case=([x+(y*z) for x,y,z in zip(average_size,case,w_percent)])
print("size+case: ",size_case)
print("w*case",[(y*z) for y,z in zip(case,w_percent)])
w_case=[(y*z) for y,z in zip(case,w_percent)]
size_case=([x+y for x,y in zip(average_size,w_case)])
print("size+case2: ",size_case)
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")      
plt.plot(np.arange(0,len(page.blocks)),average_size,label="size")
plt.legend()
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),case,label="case")
plt.legend()
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),w_percent,label="w_percent")
plt.legend()
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),[(y*z*100) for y,z in zip(case,w_percent)],label="w*case")
plt.legend()
plt.figure()
plt.ylabel("SIZE")
plt.xlabel("Block")  
plt.plot(np.arange(0,len(page.blocks)),size_case,label="size*case")
plt.legend()
plt.show()      
