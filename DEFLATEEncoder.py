from bitarray import bitarray
import binascii
import math
import sys
offset=15
lookahead=7



def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def preorderTraversal(root):
    ret = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node:
            nod=str(node)
            if len(nod)==1:
                ret.append(nod)
                ret.append(1)
                
                continue
            ret.append(0)
            stack.append(node.left)
            stack.append(node.right)
    return ret[::-1]






def findSubstring(s, char):
    index = 0
    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index

            index = index + 1

    return -1

def encode(txt, OffSet, LookSize, minMatch):
    searchBuff = ""
    lookahead = txt[:LookSize]
    txt = txt[LookSize:]
    tokens = []
    charsToTake = 0
    while len(lookahead) > 0:
        offset = 0
        length = 0
        flagBit = 0
        tmpSubstring = lookahead
        while(len(tmpSubstring) >= minMatch):
            index = findSubstring(searchBuff, tmpSubstring)
            if(index != -1):
                offset = len(searchBuff) - index
                length = len(tmpSubstring)
                flagBit = 1
                break
            else:
                tmpSubstring = tmpSubstring[:-1]
        if(flagBit == 0):
            newletter = lookahead[0]
            token = (0, newletter)
            searchBuff = searchBuff +  newletter
            charsToTake = 1
        else:
            token = (1, offset, length)
            searchBuff = searchBuff + tmpSubstring
            charsToTake = length
        searchBuff = searchBuff[-OffSet:]
        tokens.append(token)
        lookahead = lookahead[charsToTake:]
        lookahead = lookahead + txt[:charsToTake]
        txt = txt[charsToTake:]
    return (tokens)





def strFromBitArr(arr):
    st=""
    for x in arr:
        if x==False:
            st+='0'
        else:
            st+='1'
    return st


class NodeTree():

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return (self.left, self.right)



def HuffCodeTree(node, binString=''):
    if type(node) is str:
        return {node: binString}
    (l, r) = node.children()
    d = dict()
    d.update(HuffCodeTree(l, binString + '0'))
    d.update(HuffCodeTree(r, binString + '1'))
    return d

def Generate_Huff(string):
    freq = {}
    for c in string:
        if c in freq:
            freq[c] += 1
        else:
            freq[c] = 1
    

    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    nodes = freq

    while len(nodes) > 1:
        (key1, c1) = nodes[-1]
        (key2, c2) = nodes[-2]
        nodes = nodes[:-2]
        node = NodeTree(key1, key2)
        nodes.append((node, c1 + c2))

        nodes = sorted(nodes, key=lambda x: x[1], reverse=True)
    return [HuffCodeTree(nodes[0][0]),nodes[0][0]]


def ConstructBitPreOrder(p):
    a=bitarray()
    count=0
    for x in p:
        if x==1:
            a.append(True)
            bits=text_to_bits(p[count+1])
            for b in bits:
                if b=="1":
                    a.append(True)
                elif b=="0":
                    a.append(False)
        elif x==0:
            a.append(False)
        count+=1
    return a
    
def padd(arr):
    while len(arr)%8!=0:
        arr.append(False)
    return arr


def makeBitArray(arr):
    a=bitarray()
    for x in arr:
        if x=='0':
            a.append(False)
        elif x=='1':
            a.append(True)
    return a









def GenHuffCodes(H):

    huffTree=H[1]
    preOrd=preorderTraversal(huffTree)
    treeBits=bitarray()
    treeBits=ConstructBitPreOrder(preOrd)
    treeBits=treeBits+'0'
    treeLen=len(treeBits)

    treeLen=str(bin(treeLen))[2:]
    while len(treeLen)<12:
        treeLen='0'+treeLen
    treeLen=makeBitArray(treeLen)
    encodedTree=treeLen+treeBits
    return encodedTree




def blocks(string):
    freq = {}
    p=0
    for c in string:
        if c in freq:
            freq[c] += 1
        else:
            freq[c] = 1
        if len(freq)==50:
            freq={}
            p+=1



def main(argv,arc):
    fileName=argv[1][0:len(argv[1])-4]

    file = open(argv[1], "r")
    contents = file.read()
    file.close()
    
    comped=encode(contents, 2**offset-1,2**lookahead-1, 3)
    
    toGenHuff=""
    for x in comped:
        if x[0]==0:
            toGenHuff+=x[1]


   
    HuffCodes=Generate_Huff(toGenHuff)

    encodedTree=GenHuffCodes(HuffCodes)

    HuffCodes=HuffCodes[0]



    mianBits = bitarray()


    for tuble in comped:
        mianBits.append(tuble[0])
        if tuble[0]==0:
            s=HuffCodes[tuble[1]]

            
            for x in s:
                if x=='0':
                    mianBits.append(False)
                else:
                    mianBits.append(True)

        else:
            s1=str(bin(tuble[1]))
            s2=str(bin(tuble[2]))
            s1=s1[2:]
            if len(s1)<offset:
                padding="0"*(offset-len(s1))
                s1=padding+s1
            s2=s2[2:]
            if len(s2)<lookahead:
                padding="0"*(lookahead-len(s2))
                s2=padding+s2
            s=s1+s2

            for x in s:
                if x=='0':
                    mianBits.append(False)
                else:
                    mianBits.append(True)



    f = open(fileName+'.lz', 'wb')
    mianBits=encodedTree+mianBits
    l1=len(mianBits)

    mianBits=padd(mianBits)
    l2=len(mianBits)
    diff=l2-l1
    diff=bin(diff)[2:]
    while len(diff)<8:
        diff='0'+diff
    diff=makeBitArray(diff)
    mianBits=diff+mianBits


    mianBits.tofile(f)
    f.close()

if __name__ == "__main__":
    main(sys.argv,len(sys.argv))































#print(ord("a"))

