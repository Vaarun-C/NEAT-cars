#=====Library Import=====
import random

#=====class creation=====
class NEAT():
	
	#=====initialising all variables inside the class=====
	def __init__(self):
		self.mutation_rate=1
		self.mutation_rate = int(input("Please Configure the Mutation Rate:")
		self.total_population = []
		self.all_parents = []
		self.dead_caravan = []
		self.mutation_range=[start_mutation_range,stop_mutation_range]
		ele=int(input("Enter start of mutation range:"))
		ele=int(input("Enter stop of mutation range:"))
		mutation_range.append(start_mutation_range)
		mutation_range.append(start_mutation_range)

	#=====crossover_helper=====
	def crossover_helper(self, new_one, old_one):
		index = 0
		randomIndex = 0
		while(None in new_one):
			randomIndex = random.randint(0, len(old_one[0])-1)
			if(new_one[randomIndex] == None):
				new[randomIndex] = old_one[index%len(old_one)][randomIndex]
				index += 1

		return new_one
	#=====crossover=====
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

	#=====mutation=====
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

	#=====new population=====
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

#=====name condition=====
if __name__ == '__main__':
	n = NEAT()
