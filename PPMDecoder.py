
import sys




NUMSYMBOLS=129
ESC=128
MODELORDER = 4


class ArithmeticDecoding():

	def __init__(self, numbits, inp):
		self.input = inp
		self.currentbyte = 0
		self.numbitsremaining = 0
		self.NumBits = numbits
		self.FullRange = int(2**self.NumBits)
		self.HalfRange = int(self.FullRange/2)  
		self.QtrRange = int(self.HalfRange/2)
		self.BitMask = self.FullRange - 1
		self.low = 0
		self.high = self.BitMask
		self.code = 0
		for _ in range(self.NumBits):
			self.code = self.code*2 | self.ReadBitFromStream()

	def Update(self, Frequencies, symbol):
		# State check
		low = self.low
		high = self.high

		range = high - low + 1

		total = Frequencies.GetTotal()
		symlow = Frequencies.GetLow(symbol)
		symhigh = Frequencies.GetHigh(symbol)

		self.low  = low + symlow  * range // total
		self.high = low + symhigh * range // total - 1

		while ((self.low ^ self.high) & self.HalfRange) == 0:
			self.shift()
			self.low  = ((self.low*2) & self.BitMask)
			self.high = ((self.high*2) & self.BitMask) | 1

		while (self.low & ~self.high & self.QtrRange) != 0:
			self.underflow()
			self.low = (self.low*2) ^ self.HalfRange
			self.high = ((self.high ^ self.HalfRange)*2) | self.HalfRange | 1
		

	def DecodeSymbol(self, Frequencies):
		
		total = Frequencies.GetTotal()
		range = self.high - self.low + 1
		offset = self.code - self.low
		value = ((offset + 1) * total - 1) // range
		start = 0
		end = NUMSYMBOLS
		while end - start > 1:
			middle = (start + end)//2
			if Frequencies.GetLow(middle) > value:
				end = middle
			else:
				start = middle
		assert start + 1 == end
		
		symbol = start
		self.Update(Frequencies, symbol)
		return symbol
	
	def ReadFromStreem(self):
		if self.currentbyte == -1:
			return -1
		if self.numbitsremaining == 0:
			temp = self.input.read(1)
			if len(temp) == 0:
				self.currentbyte = -1
				return -1
			self.currentbyte = temp[0]
			self.numbitsremaining = 8
		assert self.numbitsremaining > 0
		self.numbitsremaining -= 1
		return (self.currentbyte >> self.numbitsremaining) & 1
	
	def shift(self):
		self.code = ((self.code*2) & self.BitMask) | self.ReadBitFromStream()
	
	
	def underflow(self):
		self.code = (self.code & self.HalfRange) | ((self.code*2) & (self.BitMask//2)) | self.ReadBitFromStream()
	
	
	def ReadBitFromStream(self):
		temp = self.ReadFromStreem()
		if temp == -1:
			temp = 0
		return temp


class OrderMinusOne():
	def __init__(self, numsyms):
		self.numsymbols = numsyms  
	def GetTotal(self):
		return self.numsymbols

	def GetLow(self, symbol):
		return symbol

	def GetHigh(self, symbol):
		return symbol + 1


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
			SubContext = CurrentContext.subcontexts
			assert SubContext is not None
			if SubContext[sym] is None:
				SubContext[sym] = ContextStruct(NUMSYMBOLS)
				SubContext[sym].frequencies.increment(ESC)
			CurrentContext = SubContext[sym]
			CurrentContext.frequencies.increment(symbol)



def main(argv):
	fileName=argv[1][0:len(argv[1])-3]
	inputfile  = argv[1]
	outputfile = fileName+'-decoded.tex'
	
	with open(inputfile, "rb") as InputStream, open(outputfile, "wb") as out:
		decompress(InputStream, out)


def decompress(InputStream, out):

	Decoder = ArithmeticDecoding(32, InputStream)
	model = PPM()
	history = []
	
	while True:
		symbol = GetNextSymbol(Decoder, model, history)
		if symbol == ESC: 
			break
		out.write(bytes(chr(symbol), 'utf-8'))
		model.UpdateContext(history, symbol)
		
		if MODELORDER >= 1:
			if len(history) ==MODELORDER:
				history.pop()
			history.insert(0, symbol)

def GetNextSymbol(dec, model, history):

	for order in reversed(range(len(history) + 1)):
		CurrentContext = model.RootContext
		for sym in history[ : order]:
			assert CurrentContext.subcontexts is not None
			CurrentContext = CurrentContext.subcontexts[sym]
			if CurrentContext is None:
				break
		else:  
			symbol = dec.DecodeSymbol(CurrentContext.frequencies)
			if symbol < ESC:
				return symbol
	return dec.DecodeSymbol(OrderMinusOne(NUMSYMBOLS))


if __name__ == "__main__":
	main(sys.argv)
