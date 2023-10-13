# Import the random library for generating random numbers
import random

# Function to configure mutation rate
def configure_mutation_rate():
    return int(input("Please configure the Mutation Rate: ")

# Function to initialize mutation range
def initialize_mutation_range():
    start_mutation_range = int(input("Enter start of mutation range: "))
    stop_mutation_range = int(input("Enter stop of mutation range: "))
    return [start_mutation_range, stop_mutation_range]

# Function to generate a random index
def generate_random_index(length):
    return random.randint(0, length - 1)

# Define a NEAT class
class NEAT:
    def __init__(self):
        # Initialize mutation rate with a default value of 1
        self.mutation_rate = 1
        
        # Prompt the user to configure the mutation rate
        self.mutation_rate = configure_mutation_rate()
        
        # Initialize lists to store populations and parents
        self.total_population = []
        self.all_parents = []
        self.dead_caravan = []

        # Initialize mutation range with user-defined start and stop values
        self.mutation_range = initialize_mutation_range()

    # Helper function for crossover
    def crossover_helper(self, new_one, old_one):
        index = 0
        randomIndex = 0
        while None in new_one:
            old_one = input
            rand_gen()
            if new_one[randomIndex] is None:
                new_one[randomIndex] = old_one[index % len(old_one)][randomIndex]
                index += 1
        return new_one

    # Perform crossover operation
    def crossover(self):
        weights = []
        biases = []
        for parent in self.parents:
            w_and_b = parent.brain.getWeightsAndBiases()
            weights.append(w_and_b[0])
            biases.append(w_and_b[1])

        for i in range(len(self.dead_caravan)):
            newWeights = self.crossover_helper([None] * len(weights[0]), weights)
            newBiases = self.crossover_helper([None] * len(biases[0]), biases)
            self.population.append((newWeights, newBiases))

    # Perform mutation operation
    def mutation(self):
        for entity_w_b in self.population:
            if random.choices([True, False], weights=[self.mutation_rate, 1 - self.mutation_rate])[0]:
                for index, weight in enumerate(entity_w_b[0]):
                    add_or_sub = random.choice([1, -1])
                    entity_w_b[0][index] = weight + add_or_sub * random.uniform(self.mutation_range[0], self.mutation_range[1])

            if random.choices([True, False], weights=[self.mutation_rate, 1 - self.mutation_rate])[0]:
                for index, biase in enumerate(entity_w_b[1]):
                    add_or_sub = random.choice([1, -1])
                    entity_w_b[1][index] = biase + add_or_sub * random.uniform(self.mutation_range[0], self.mutation_range[1])

    # Create a new population with updated weights and biases
    def newPopulation(self, parents, dead_caravan):
        if len(parents) == 0:
            return []

        self.population = []
        self.parents = parents
        self.dead_caravan = dead_caravan
        self.crossover()
        self.mutation()

        for index, dead_car in enumerate(self.dead_caravan):
            dead_car.reset()
            dead_car.brain.setWeightsAndBiases(self.population[index])

        return self.dead_caravan

# Entry point for the script
if __name__ == '__main__':
    n = NEAT()

