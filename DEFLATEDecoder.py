from bitarray import bitarray
import binascii
import math
import sys

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

class NodeTree():

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return (self.left, self.right)

    def nodes(self):
        return (self.left, self.right)

    def __str__(self):
        return '%s%s' % (self.left, self.right)

def huffman_code_tree(node, binString=''):
    if type(node) is str:
        return {binString: node}
    (l, r) = node.children()
    d = dict()
    d.update(huffman_code_tree(l, binString + '0'))
    d.update(huffman_code_tree(r, binString + '1'))
    return d











def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'
def decode(tok):

    decoded = ""
    for token in tok:

        flagBit = token[0]
        if flagBit == 0:
            decoded = decoded + token[1]

        else:
            offset = token[1]
            length = token[2]

            start = len(decoded) - offset
            end = start + length
            stringToAdd = decoded[start:end]

            stringToAdd = stringToAdd[:length]

            decoded = decoded + stringToAdd

    return decoded

def strFromBitArr(arr):
    st=""
    for x in arr:
        if x==False:
            st+='0'
        else:
            st+='1'
    return st




def main(argv,arc):
    fileName=argv[1][0:len(argv[1])-3]
  
    f = open(argv[1], 'rb')
    tokens=[]
    bits = bitarray()
    bits.fromfile(f,-1)
    pad=strFromBitArr(bits[0:8])
    bits=bits[8:]

    padding=int(pad,2)
    treeBitsLenInBin=strFromBitArr(bits[0:12])
    treeBitsLen=int(treeBitsLenInBin,2)
    treeBits=strFromBitArr(bits[12:12+treeBitsLen])
    preOrdTree=[]
    
    count=0
    while count<treeBitsLen:
        if treeBits[count]=="1":
            preOrdTree.append(1)
            letter=text_from_bits(treeBits[count+1:count+9])
            preOrdTree.append(letter)
            count+=9
        elif treeBits[count]=="0":
            preOrdTree.append(0)
            count+=1
        
    stack = []
    count=0
    for x in preOrdTree:
        if x==1:
            stack.append(preOrdTree[count+1])
        elif x==0 and len(stack)>1:
            key1=stack.pop()
            key2=stack.pop()
            node = NodeTree(key2, key1)
            stack.append(node)
        count+=1
    HuffCodes=huffman_code_tree(stack[0])

    f.close()
    bits=bits[12+treeBitsLen:len(bits)]

    length=len(bits)

    count=0

    while count<length-padding:
   
        if bits[count]==False:

            st=""
            for x in range(count+1,count+25):

                if bits[x]==False:
                    st+='0'
                else:
                    st+='1'
                if st in HuffCodes:
                    #print("yrsd")
                    tokens.append((0,HuffCodes[st]))
                    #print(tokens)
                    count=x+1
                    break

                
        elif bits[count]==True:
            st=""
            for x in range(count+1,count+16):
                if bits[x]==False:
                    st+='0'
                else:
                    st+='1'
            num=int(st,2)
            st=""
            for x in range(count+16,count+23):
                if bits[x]==False:
                    st+='0'
                else:
                    st+='1'
            num1=int(st,2)
            count+=23
            tokens.append((1,num,num1))
            
    #print(tokens)

    s=decode(tokens)

    #print(s)

    f = open(fileName+'-decoded.tex', 'w')
    f.write(s)
    f.close


if __name__ == "__main__":
    main(sys.argv,len(sys.argv))