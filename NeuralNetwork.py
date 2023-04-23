import random
import math

class Layer():
	def __init__(self, inputCount, outputCount):
		self.inputCount = inputCount
		self.outputCount = outputCount
		self.inputs = [0]*self.inputCount
		self.outputs = [0]*self.outputCount
		self.biases = [0]*self.outputCount
		self.weights = [[0]*self.outputCount for _ in range(self.inputCount)]

		self.randomize()

	def randomize(self):

		for i in range(self.inputCount):
			for j in range(self.outputCount):
				self.weights[i][j] = random.uniform(-1, 1)

		for i in range(self.outputCount):
			self.biases[i] = random.uniform(-1, 1)

	def feedForward(self, givenInputs):
		for i in range(self.inputCount):
			self.inputs[i] = givenInputs[i]

		for i in range(self.outputCount):
			weightedSum = 0
			for j in range(self.inputCount):
				weightedSum += self.inputs[j]*self.weights[j][i]
			self.outputs[i] = math.tanh(weightedSum+self.biases[i])

		return self.outputs

	def setWeights(self, newweights):
		for i in range(self.inputCount):
			for j in range(self.outputCount):
				self.weights[i][j] = newweights[i*self.outputCount+j]

	def setBiases(self, newbiases):
		for i in range(self.outputCount):
			self.biases[i] = newbiases[i]

	def __repr__(self) -> str:
		return f"Layer({self.inputCount},{self.outputCount})"

class NN:
	def __init__(self, neurons):
		self.layers = []
		for i in range(len(neurons)-1):
			self.layers.append(Layer(neurons[i], neurons[i+1]))

	def feedForward(self, network, givenInputs):

		mean = sum(givenInputs)/len(givenInputs)
		stdev = (sum([(x-mean)**2 for x in givenInputs])/len(givenInputs))**0.5

		if stdev == 0:
			oldRange = 1440 - 0;
			newRange = 3 - -3;
			z = [(((newRange * (x - 0)) / oldRange) + -3) for x in givenInputs];
			print(f"Standard deviation is zero")
		else:
			z = [(x-mean)/stdev for x in givenInputs]

		outputs = network.layers[0].feedForward(z)

		for layer in network.layers[1:]:
			outputs = layer.feedForward(outputs)

		return outputs

	def getWeightsAndBiases(self):
		weight_array = []
		biase_array = [biases for biasesrow in [layer.biases for layer in self.layers] for biases in biasesrow]

		for weights in [layer.weights for layer in self.layers]:
			weight_array+=[weight for weightrow in weights for weight in weightrow]

		return (weight_array, biase_array)

	def setWeightsAndBiases(self, weights_and_biases):
		index = 0
		for layer in self.layers:
			layer.setWeights(weights_and_biases[0][index:index + layer.inputCount*layer.outputCount])
			index += layer.inputCount*layer.outputCount

		index = 0
		for layer in self.layers:
			layer.setBiases(weights_and_biases[1][index:index + layer.outputCount])
			index += layer.outputCount
