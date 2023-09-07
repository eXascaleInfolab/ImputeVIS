# For the thesis
import numpy as np
import torch
import matplotlib.pyplot as plt

# Source: https://www.kaggle.com/code/markwallbang/m-rnn-estimate-missing-values-in-time-series
# Generate the dummy dataset
np.random.seed(123)
f = np.array([1.5,2,2.5])
offset = np.array([0,1,2]).reshape(-1,1)
w = 2. * np.pi * f
t = np.linspace(0, 1, 50)
x = torch.tensor(np.sin(w.reshape(-1,1) * t)+offset).float()
ground_truth = x.detach().clone()
mask = torch.ones_like(x)
delta = torch.ones_like(x).float()
delta[:,0] = 0

# remove 5% of the data
ix = [(channel,t) for channel in range(x.shape[0]) for t in range(x.shape[1])]
np.random.shuffle(ix)
to_replace = int(round(.05*len(ix)))
ix = ix[:to_replace]
for idx in ix:
    x[idx[0],idx[1]] = np.nan
    mask[idx[0],idx[1]] = 0

plt.figure(figsize=(12,4))
plt.title("Dummy dataset")
plt.xlabel("t")
plt.ylabel("Measurement")
for i in range(3):
    plt.plot(t*50,x[i].cpu())
    plt.plot(t*50,ground_truth[i].cpu(),alpha=0.4,c="grey",linestyle='dashed')

###############################
# Corrected matrices and vectors
A1_corrected = np.array([[0, -0.59, -0.40],
                         [0.07, 0, 0.75],
                         [-0.14, 0.09, 0]])

v1_corrected = np.array([[2], [4], [3]])

A2_corrected = np.array([[-0.41, -0.49, 0.08],
                         [0.14, 0.14, -0.14],
                         [-0.51, -0.54, -0.04]])

v2_corrected = np.array([[1.13], [0.57], [1.64]])

A3_corrected = np.array([[-0.22, -0.64, -0.44],
                         [0.53, -0.01, -0.52],
                         [-0.38, -0.88, -0.56]])

v3_corrected = np.array([[1], [1], [1]])

v4_corrected = np.array([[-0.21], [0.62], [-0.17]])

# Compute the matrix-vector multiplications and sum them using the corrected values
result_corrected = (np.dot(A1_corrected, v1_corrected) + np.dot(A2_corrected, v2_corrected) +
                    np.dot(A3_corrected, v3_corrected) + v4_corrected)

# Apply ReLU function
relu_result_corrected = np.maximum(0, result_corrected)
relu_result_corrected
#result array([-2.89952524,  1.89142254, -2.13751819])

###################
# Given matrices and vectors
W = np.array([[-0.1957, -0.0024, -0.3857],
              [0.0047, 0.5593, -0.2730],
              [-0.0396, 0.5180, 0.2218]])

h_13 = np.array([[0], [3], [0]])
alpha = np.array([[0.5846], [0.3176], [0.49670]])

# Compute the matrix-vector multiplication and add the bias
x_hat_13 = W.dot(h_13) + alpha
x_hat_13
# Result: array([[0.5774],
#        [1.9955],
#        [2.0507]])

###################
# Rounded matrices and vectors
W_rounded = np.array([[-0.19, -0, -0.39],
                      [0, 0.56, -0.27],
                      [-0.04, 0.52, 0.22]])

alpha_rounded = np.array([[0.58], [0.32], [0.50]])

# Compute the matrix-vector multiplication and add the bias using rounded values
x_hat_13_rounded = W_rounded.dot(h_13) + alpha_rounded
x_hat_13_rounded
# array([[0.58],
#        [2.  ],
#        [2.06]])
