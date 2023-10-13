#=====Library Import=====
import random

#=====class creation=====
class NEAT():
	def __init__(self):
		self.mutation_rate = 0.05
		self.population = []
		self.parents = []
		self.dead_caravan = []
		self.mutation_range = [-1, 1]

	def crossover_helper(self, new, old):
		index = 0
		randomIndex = 0
		while(None in new):
			randomIndex = random.randint(0, len(old[0])-1)
			if(new[randomIndex] == None):
				new[randomIndex] = old[index%len(old)][randomIndex]
				index += 1

		return new

	def crossover(self):
		weights = []
		biases = []
		for parent in self.parents:
			w_and_b = parent.brain.getWeightsAndBiases()
			weights.append(w_and_b[0])
			biases.append(w_and_b[1])

		for i in range(len(self.dead_caravan)):
			newWeights = self.crossover_helper([None]*len(weights[0]), weights)
			newBiases = self.crossover_helper([None]*len(biases[0]), biases)
			self.population.append((newWeights, newBiases))

	def mutation(self):
		for entity_w_b in self.population:
			if(random.choices([True, False], weights=[self.mutation_rate, 1-self.mutation_rate])[0]):
				for index, weight in enumerate(entity_w_b[0]):
					add_or_sub = random.choice([1, -1])
					# entity_w_b[0][index] = random.uniform(self.mutation_range[0], self.mutation_range[1])
					entity_w_b[0][index] = weight + add_or_sub*random.uniform(self.mutation_range[0], self.mutation_range[1])

			if(random.choices([True, False], weights=[self.mutation_rate, 1-self.mutation_rate])[0]):
				for index, biase in enumerate(entity_w_b[1]):
					add_or_sub = random.choice([1, -1])
					# entity_w_b[1][index] = random.uniform(self.mutation_range[0], self.mutation_range[1])
					entity_w_b[1][index] = biase + add_or_sub*random.uniform(self.mutation_range[0], self.mutation_range[1])

	def newPopulation(self, parents, dead_caravan):
		if len(parents) == 0: return []
		self.population = []
		self.parents = parents
		self.dead_caravan = dead_caravan
		self.crossover()
		self.mutation()
		for index, dead_car in enumerate(self.dead_caravan):
			dead_car.reset()
			dead_car.brain.setWeightsAndBiases(self.population[index])
		return self.dead_caravan #which is now revived with new weights and biases

if __name__ == '__main__':
	n = NEAT()
