import numpy as np

rows = -1

def tanh(x):
    return np.tanh(x)

def deriv_tanh(x):
    return 1 / (np.cosh(x) ** 2)

def softmax(Z):
    A = np.exp(Z) / sum(np.exp(Z))
    return A

# structure is a tuple with the number of nuerons per layer
# (784, 16, 10)
def init_network(structure):
    all_weights = []
    all_biases  = []
    prev = -1
    for n in structure:
        if prev == -1: 
            prev = n
            continue

        # if len(all_weights) == 0:
        #     all_weights = np.random.rand(n, prev) - 0.5
        # if len(all_biases) == 0:
        #     all_weights = np.random.rand(n, 1) - 0.5

        all_weights.append(np.random.rand(n, prev) - 0.5)
        all_biases.append(np.random.rand(n, 1) - 0.5)
        prev = n

    return (all_weights, all_biases)


# network is a tuple of all weights and biases
# same data type as returned by init_network
# returns tuple of the sums, activations (size will be 1 less than the number of layers)
# inputs need to be shape (n, 1). Can be done by transposing the input
# activations will have the inputs as the first element
def feed_forward(inputs, network: tuple[list, list]):
    sums = [inputs]
    activations = [inputs]
    weights, biases = network[0], network[1]
    assert len(weights) == len(biases)

    prev_layer = np.array(inputs)
    for i in range(len(weights)):
        W = np.array(weights[i])
        B = np.array(biases[i])

        A = []
        # W = np.array(W).T # need to transpose to make the matrix dimensions work
        # print(f"{W.shape} @ {prev_layer.shape} + {B.shape}")
        Z = W @ prev_layer
        for i, (z, b) in enumerate(zip(Z, B)):
            Z[i] = z + b

        sums.append(Z)
        if i == len(weights) - 1:
            A = softmax(Z)
        else:
            A = tanh(Z)
        activations.append(A) 
        prev_layer = A

    return sums, activations

def one_hot(Y):
    one_hot_Y = np.zeros((Y.size, Y.max() + 1))
    one_hot_Y[np.arange(Y.size), Y] = 1
    return one_hot_Y.T

def loss(Y, activations):
    return activations[0] - one_hot(Y)

def backward_propagation(Y, sums, activations, weights, biases):
    if rows == -1: raise Exception("Number of rows in data was not defined (can't be -1)")

    # first one will be that of the final layer
    sums = sums[::-1]
    activations = activations[::-1] 
    weights = weights[::-1]
    biases = biases[::-1]

    dWeights = [] 
    dBiases  = []
    
    dZ = loss(Y, activations)
    for i, W in enumerate(weights):
        if not (i < len(activations) - 1): break
        dW = (dZ @ activations[i + 1].T) / rows 
        dWeights.append(dW)

        dB = np.sum(dZ) / rows
        dBiases.append(dB)

        dZ = (W.T @ dZ) * deriv_tanh(sums[i + 1])

    # these are in reverse order. They need to be iterated through in reverse
    return dWeights, dBiases

def update_params(weights, biases, dWeights, dBiases, lr):
    new_weights, new_biases = [], []
    
    for w, b, dw, db in zip(weights, biases, dWeights[::-1], dBiases[::-1]): # reverse dWeights & dBiases into correct order
        new_weights.append(w - (lr * dw))
        new_biases.append (b - (lr * db))

    return new_weights, new_biases

def gradient_descent(X, Y, learning_rate: float, iterations: int, network: tuple[list, list]):
    weights, biases = network[0], network[1]

    for i in range(iterations):
        sums, activations = feed_forward(X, (weights, biases))
        dWeights, dBiases = backward_propagation(Y, sums, activations, weights, biases)
        weights, biases = update_params(weights, biases, dWeights, dBiases, learning_rate)
        if i % 10 == 0:
            print("Iteration: ", i)
            predictions = get_predictions(activations[-1])
            print(get_accuracy(predictions, Y))

    return weights, biases

def get_predictions(output):
    return np.argmax(output, 0)

def get_accuracy(predictions, Y):
    return np.sum(predictions == Y) / Y.size

def make_predictions(inputs, weights, biases):
    _, activations = feed_forward(inputs, (weights, biases))
    predictions = get_predictions(activations[-1])
    return predictions

def download_model(W1, B1, W2, B2, name):
    master = np.array([W1, B1, W2, B2], dtype=object)
    np.save(f"models/{name}/master.npy", master)
    return

def flatten_output(O):
    flat = np.zeros(10)
    for i, _ in enumerate(O):
        flat[i] = O[i][0]
    return flat