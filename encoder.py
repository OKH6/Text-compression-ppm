
import sys

NUMSYMBOLS=129
ESC=128
MODELORDER = 4



class ArithmeticEncoding:
	def __init__(self, numbits, OutputStream):
		self.output = OutputStream  
		self.currentbyte = "" 
		self.BitsFilled = 0  
		self.NumBits = numbits
		self.FullRange = int(2**self.NumBits)
		self.HalfRange = int(self.FullRange/2)  
		self.QtrRange = int(self.HalfRange/2)
		self.BitMask = self.FullRange - 1
		self.low = 0
		self.high = self.BitMask
		self.UnderflowBits = 0
	
	def GenCode(self, Frequencies, symbol):
		low = self.low
		high = self.high
		range = high - low + 1
		total = Frequencies.GetTotal()
		symlow = Frequencies.GetLow(symbol)
		symhigh = Frequencies.GetHigh(symbol)
		self.low  = low + symlow  * range // total
		self.high = low + symhigh * range // total - 1
		#print("------------------------------------------")
		
		while ((self.low ^ self.high) & self.HalfRange) == 0:
			self.shift()
			self.low  = ((self.low*2) & self.BitMask)
			self.high = ((self.high*2) & self.BitMask) | 1
		
		while (self.low & ~self.high & self.QtrRange) != 0:
			self.underflow()
			self.low = (self.low*2) ^ self.HalfRange
			self.high = ((self.high ^ self.HalfRange)*2) | self.HalfRange | 1

	def finish(self):
		self.write(1)
	
	
	def shift(self):
		#bit=int(bin(self.low)[2])
		bit = self.low >> (self.NumBits - 1)
		
		self.write(bit)
		for i in range(self.UnderflowBits):
			#print(i)
			self.write(bit ^ 1)
		
		self.UnderflowBits = 0
	
	
	def underflow(self):
		self.UnderflowBits += 1

	def write(self, b):
		self.currentbyte += str(b)
		self.BitsFilled += 1
		if self.BitsFilled == 8:
			bb=int(self.currentbyte, 2)
			towrite = bytes((bb,))
			self.output.write(towrite)
			self.currentbyte = ""
			self.BitsFilled = 0
	def CloseBitStream(self):
		while self.BitsFilled != 0:
			self.write(0)
		self.output.close()


class FrequencyTable():

	def __init__(self, Frequencies):
		self.frequencies = list(Frequencies) 

		self.total = sum(self.frequencies)
		
		self.cumulative = None

	def get(self, symbol):
		return self.frequencies[symbol]
	
	
	def increment(self, symbol):
		self.total += 1
		self.frequencies[symbol] += 1
		self.UpdateCumFrequencies()
	

	def GetTotal(self):
		return self.total
	

	def GetLow(self, symbol):
		return self.cumulative[symbol]
	

	def GetHigh(self, symbol):
		return self.cumulative[symbol + 1]
	
	def UpdateCumFrequencies(self):
		NewFreqs = [0]
		CurSum = 0
		for freq in self.frequencies:
			CurSum += freq
			NewFreqs.append(CurSum)
		self.cumulative = NewFreqs
	






class OrderMinusOne():
	def __init__(self, numsyms):
		self.numsymbols = numsyms  
	def GetTotal(self):
		return self.numsymbols

	def GetLow(self, symbol):
		return symbol

	def GetHigh(self, symbol):
		return symbol + 1


class ContextStruct:
	def __init__(self, NUMsymbols):
		self.frequencies = FrequencyTable([0] * NUMsymbols)
		self.subcontexts = ([None] * NUMsymbols)


class PPM:
	def __init__(self):
		self.RootContext = ContextStruct(NUMSYMBOLS)
		self.RootContext.frequencies.increment(ESC)
		
	def UpdateContext(self, history, symbol):

		CurrentContext = self.RootContext
		
		CurrentContext.frequencies.increment(symbol)
		for sym in history:
			subctxs = CurrentContext.subcontexts
			assert subctxs is not None
			if subctxs[sym] is None:
				subctxs[sym] = ContextStruct(NUMSYMBOLS)
				subctxs[sym].frequencies.increment(ESC)
			CurrentContext = subctxs[sym]
			CurrentContext.frequencies.increment(symbol)
	

def main(argv):
	fileName=argv[1][0:len(argv[1])-4]
	inputfile  = argv[1]
	outputfile = fileName+".lz"
	inp= open(inputfile, "rb") 
	out=open(outputfile, "wb")
	compress(inp, out)


def compress(inp, out):
	encoder = ArithmeticEncoding(32, out)
	PPMOrder = PPM()
	history = []
	
	while True:
		symbol = inp.read(1)
		if len(symbol) == 0:
			break
		#Get ASCII NUM
		symbol = symbol[0]
		ProcessSymbol(PPMOrder, history, symbol, encoder)
		PPMOrder.UpdateContext(history, symbol)
		if MODELORDER >= 1:
			if len(history) ==MODELORDER:
				history.pop()
			history.insert(0, symbol)
	ProcessSymbol(PPMOrder, history, ESC, encoder)  
	encoder.finish()
	encoder.CloseBitStream()


def ProcessSymbol(PPMOrder, history, symbol, encoder):
	for order in reversed(range(len(history) + 1)):
		CurrentContext = PPMOrder.RootContext
		for sym in history[ : order]:
			assert CurrentContext.subcontexts is not None
			CurrentContext = CurrentContext.subcontexts[sym]
			if CurrentContext is None:
				break
		else: 
			if symbol != ESC and CurrentContext.frequencies.get(symbol) > 0:
				encoder.GenCode(CurrentContext.frequencies, symbol)
				return
			encoder.GenCode(CurrentContext.frequencies, ESC)

	encoder.GenCode(OrderMinusOne(NUMSYMBOLS), symbol)

if __name__ == "__main__":
	main(sys.argv)
