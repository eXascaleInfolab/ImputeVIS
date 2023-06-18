'''
Jinsung Yoon (06/19/2018)
M-RNN Architecture (Updated)
'''

#%% Necessary Packages
import tensorflow as tf
import numpy as np

from tensorflow.python.framework import ops

#%% Main Function


def M_RNN(trainZ, trainM, trainT, testZ, testM, testT, hidden_dim=10, learning_rate=0.01, iterations=1000, keep_prob_var=1.0):

    # Graph Initialization
    ops.reset_default_graph()

    #%% Parameters
    seq_length = len(trainZ[0,:,0])
    feature_dim = len(trainZ[0,0,:])
    # hidden_dim = 10   # hidden state dimension, default = 10

    # learning_rate = 0.01  # learning rate, default = 0.01
    # iterations = 1000  # iterations, default = 1000

    #%% input place holders (Y: target, M: Mask)
    tf.compat.v1.disable_eager_execution()  # Added for compatibility
    Y = tf.compat.v1.placeholder(tf.float32, [seq_length, None, 1])
    M = tf.compat.v1.placeholder(tf.float32, [seq_length, None, 1])

    #%% Weights Initialization

    class Bi_GRU_cell(object):

        """
        Bi-directional GRU cell object which takes 3 arguments for initialization.
        input_size = Input Vector size
        hidden_layer_size = Hidden layer size
        target_size = Output vector size
        """

        def __init__(self, input_size, hidden_layer_size, target_size):

            # Initialization of given values
            self.input_size = input_size
            self.hidden_layer_size = hidden_layer_size
            self.target_size = target_size

            # Weights and Bias for input and hidden tensor for forward pass
            self.Wr = tf.Variable(tf.zeros([self.input_size, self.hidden_layer_size]))
            self.Ur = tf.Variable(tf.zeros([self.hidden_layer_size, self.hidden_layer_size]))
            self.br = tf.Variable(tf.zeros([self.hidden_layer_size]))

            self.Wu = tf.Variable(tf.zeros([self.input_size, self.hidden_layer_size]))
            self.Uu = tf.Variable(tf.zeros([self.hidden_layer_size, self.hidden_layer_size]))
            self.bu = tf.Variable(tf.zeros([self.hidden_layer_size]))

            self.Wh = tf.Variable(tf.zeros([self.input_size, self.hidden_layer_size]))
            self.Uh = tf.Variable(tf.zeros([self.hidden_layer_size, self.hidden_layer_size]))
            self.bh = tf.Variable(tf.zeros([self.hidden_layer_size]))

            # Weights and Bias for input and hidden tensor for backward pass
            self.Wr1 = tf.Variable(tf.zeros([self.input_size, self.hidden_layer_size]))
            self.Ur1 = tf.Variable(tf.zeros([self.hidden_layer_size, self.hidden_layer_size]))
            self.br1 = tf.Variable(tf.zeros([self.hidden_layer_size]))

            self.Wu1 = tf.Variable(tf.zeros([self.input_size, self.hidden_layer_size]))
            self.Uu1 = tf.Variable(tf.zeros([self.hidden_layer_size, self.hidden_layer_size]))
            self.bu1 = tf.Variable(tf.zeros([self.hidden_layer_size]))

            self.Wh1 = tf.Variable(tf.zeros([self.input_size, self.hidden_layer_size]))
            self.Uh1 = tf.Variable(tf.zeros([self.hidden_layer_size, self.hidden_layer_size]))
            self.bh1 = tf.Variable(tf.zeros([self.hidden_layer_size]))

            # Weights for output layers
            self.Wo = tf.Variable(tf.compat.v1.truncated_normal([self.hidden_layer_size * 2, self.target_size], mean=0, stddev=.01))
            self.bo = tf.Variable(tf.compat.v1.truncated_normal([self.target_size], mean=0, stddev=.01))

            # Placeholder for input vector with shape[batch, seq, embeddings]
            self._inputs = tf.compat.v1.placeholder(tf.float32, shape=[None, None, self.input_size], name='inputs')

            # Reversing the inputs by sequence for backward pass of the GRU
            self._inputs_rev = tf.compat.v1.placeholder(tf.float32, shape=[None, None, self.input_size], name='inputs')

            # Processing inputs to work with scan function
            self.processed_input = process_batch_input_for_RNN(self._inputs)

            # For bacward pass of the GRU
            self.processed_input_rev = process_batch_input_for_RNN(self._inputs_rev)

            '''
            Initial hidden state's shape is [1,self.hidden_layer_size]
            In First time stamp, we are doing dot product with weights to
            get the shape of [batch_size, self.hidden_layer_size].
            For this dot product tensorflow use broadcasting. But during
            Back propagation a low level error occurs.
            So to solve the problem it was needed to initialize initial
            hiddden state of size [batch_size, self.hidden_layer_size].
            So here is a little hack !!!! Getting the same shaped
            initial hidden state of zeros.
            '''

            self.initial_hidden = self._inputs[:, 0, :]
            self.initial_hidden = tf.matmul(self.initial_hidden, tf.zeros([input_size, hidden_layer_size]))

        # Function for Forward GRU cell.
        def GRU_f(self, previous_hidden_state, x):
            """
            This function takes previous hidden state
            and memory tuple with input and
            outputs current hidden state.
            """

            # R Gate
            r = tf.sigmoid(tf.matmul(x, self.Wr) + tf.matmul(previous_hidden_state, self.Ur) + self.br)

            # U Gate
            u = tf.sigmoid(tf.matmul(x, self.Wu) + tf.matmul(previous_hidden_state, self.Uu) + self.bu)

            # Final Memory cell
            c = tf.tanh(tf.matmul(x, self.Wh) + tf.matmul( tf.multiply(r, previous_hidden_state), self.Uh) + self.bh)

            # Current Hidden state
            current_hidden_state = tf.multiply( (1 - u), previous_hidden_state ) + tf.multiply( u, c )

            return current_hidden_state


        # Function for Forward GRU cell.
        def GRU_b(self, previous_hidden_state, x):
            """
            This function takes previous hidden
            state and memory tuple with input and
            outputs current hidden state.
            """

            r = tf.sigmoid(tf.matmul(x, self.Wr1) + tf.matmul(previous_hidden_state, self.Ur1) + self.br1)

            # U Gate
            u = tf.sigmoid(tf.matmul(x, self.Wu1) + tf.matmul(previous_hidden_state, self.Uu1) + self.bu1)

            # Final Memory cell
            c = tf.tanh(tf.matmul(x, self.Wh1) + tf.matmul( tf.multiply(r, previous_hidden_state), self.Uh1) + self.bh1)

            # Current Hidden state
            current_hidden_state = tf.multiply( (1 - u), previous_hidden_state ) + tf.multiply( u, c )

            return current_hidden_state

        # Function to get the hidden and memory cells after forward pass
        def get_states_f(self):
            """
            Iterates through time/ sequence to get all hidden state
            """

            # Getting all hidden state through time
            all_hidden_states = tf.scan(self.GRU_f, self.processed_input, initializer=self.initial_hidden, name='states')

            return all_hidden_states

        # Function to get the hidden and memory cells after backward pass
        def get_states_b(self):
            """
            Iterates through time/ sequence to get all hidden state
            """

            all_hidden_memory_states = tf.scan(self.GRU_b, self.processed_input_rev, initializer=self.initial_hidden, name='states')

            # Now reversing the states to keep those in original order
            all_hidden_states = tf.reverse(all_hidden_memory_states, [1])

            return all_hidden_states

        # Function to concat the hiddenstates for backward and forward pass
        def get_concat_hidden(self):

            # Getting hidden and memory for the forward pass
            all_hidden_states_f = self.get_states_f()

            # Getting hidden and memory for the backward pass
            all_hidden_states_b = self.get_states_b()

            # Concating the hidden states of forward and backward pass
            concat_hidden = tf.concat([all_hidden_states_f, all_hidden_states_b],2)

            return concat_hidden

        # Function to get output from a hidden layer
        def get_output(self, hidden_state):
            """
            This function takes hidden state and returns output
            """
            output = tf.nn.sigmoid(tf.matmul(hidden_state, self.Wo) + self.bo)

            return output

        # Function for getting all output layers
        def get_outputs(self):
            """
            Iterating through hidden states to get outputs for all timestamp
            """
            all_hidden_states = self.get_concat_hidden()

            all_outputs = tf.map_fn(self.get_output, all_hidden_states)

            return all_outputs


    # Function to convert batch input data to use scan ops of tensorflow.
    def process_batch_input_for_RNN(batch_input):
        """
        Process tensor of size [5,3,2] to [3,5,2]
        """
        batch_input_ = tf.transpose(batch_input, perm=[2, 0, 1])
        X = tf.transpose(batch_input_)

        return X


    # Initializing rnn object
    rnn = Bi_GRU_cell(3, hidden_dim, 1)

    # Getting all outputs from rnn
    outputs = rnn.get_outputs()

    # reshape out for sequence_loss
    loss = tf.sqrt(tf.reduce_mean(tf.square(M*outputs - M*Y)))

    #
    optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate)
    train = optimizer.minimize(loss)

    # Output Initialization
    final_results_train = np.zeros([len(trainZ), seq_length, feature_dim])
    final_results_test = np.zeros([len(testZ), seq_length, feature_dim])

    # Sessions
    sess = tf.compat.v1.Session()

    for f in range(feature_dim):
        sess.run(tf.compat.v1.global_variables_initializer())

        # Training step
        for i in range(iterations):

            Input_Temp = np.dstack((trainZ[:,:,f],trainM[:,:,f],trainT[:,:,f]))

            Input_Temp_Rev = np.flip(Input_Temp, 1)

            Input = np.zeros([len(trainZ), seq_length, 3])
            Input[:,1:,:] = Input_Temp[:,:6,:]

            Input_Rev = np.zeros([len(trainZ), seq_length, 3])
            Input_Rev[:,1:,:] = Input_Temp_Rev[:,:6,:]

            _, step_loss = sess.run([train, loss], feed_dict={M: np.transpose(np.dstack(trainM[:,:,f]),[1, 2, 0]),
                                    Y: np.transpose(np.dstack(trainZ[:,:,f]),[1, 2, 0]),
                                    rnn._inputs: Input, rnn._inputs_rev: Input_Rev})

        #%% Fill in the missing values
        #Train prediction

        Input_Temp = np.dstack((trainZ[:,:,f],trainM[:,:,f],trainT[:,:,f]))

        Input_Temp_Rev = np.flip(Input_Temp, 1)

        Input = np.zeros([len(trainZ), seq_length, 3])
        Input[:,1:,:] = Input_Temp[:,:(seq_length-1),:]

        Input_Rev = np.zeros([len(trainZ), seq_length, 3])
        Input_Rev[:,1:,:] = Input_Temp_Rev[:,:(seq_length-1),:]

        train_predict = sess.run(outputs, feed_dict={rnn._inputs: Input, rnn._inputs_rev: Input_Rev})
        final_results_train[:,:,f] = np.transpose(np.squeeze(train_predict))

        # Test prediction

        Input_Temp = np.dstack((testZ[:,:,f],testM[:,:,f],testT[:,:,f]))
        Input_Temp_Rev = np.flip(Input_Temp, 1)

        Input = np.zeros([len(testZ), seq_length, 3])
        Input[:,1:,:] = Input_Temp[:,:(seq_length-1),:]

        Input_Rev = np.zeros([len(testZ), seq_length, 3])
        Input_Rev[:,1:,:] = Input_Temp_Rev[:,:(seq_length-1),:]

        test_predict = sess.run(outputs, feed_dict={rnn._inputs: Input, rnn._inputs_rev: Input_Rev})
        final_results_test[:,:,f] = np.transpose(np.squeeze(test_predict))

    #%% Initial point interpolation (Only for the performance)
    # If the first variable is missing, interpolate

    for i in range(len(trainZ[:,0,0])):
        for k in range(len(trainZ[0,0,:])):
            for j in range(len(trainZ[0,:,0])):
                if (trainT[i,j,k] > j):
                    idx = np.where(trainM[i,:,k]==1)[0]
                    if (np.size(idx) != 0):
                        final_results_train[i,j,k] = trainZ[i,np.min(idx),k]


    for i in range(len(testZ[:,0,0])):
        for k in range(len(testZ[0,0,:])):
            for j in range(len(testZ[0,:,0])):
                if (testT[i,j,k] > j):
                    idx = np.where(testM[i,:,k]==1)[0]
                    if (np.size(idx) != 0):
                        final_results_test[i,j,k] = testZ[i,np.min(idx),k]

    #%%
    output_train = final_results_train
    output_test = final_results_test


    #%% Fully Connected Layers

    # Change the data structure
    Train_No = len(trainZ[:,0,0])
    Test_No = len(testZ[:,0,0])
    Seq_No = len(trainZ[0,:,0])
    Dim_No = len(trainZ[0,0,:])

    rec_trainZ = final_results_train
    rec_testZ = final_results_test

    col_trainZ = np.reshape(trainZ, [Train_No * Seq_No, Dim_No])
    col_rec_trainZ = np.reshape(rec_trainZ, [Train_No * Seq_No, Dim_No])

    col_testZ = np.reshape(testZ, [Test_No * Seq_No, Dim_No])
    col_rec_testZ = np.reshape(rec_testZ, [Test_No * Seq_No, Dim_No])

    col_trainM = np.reshape(trainM, [Train_No * Seq_No, Dim_No])
    col_testM = np.reshape(testM, [Test_No * Seq_No, Dim_No])

    # train Parameters
    ops.reset_default_graph()

    feature_dim = Dim_No

    learning_rate = 0.01
    iterations = 4000

    hidden_no = Dim_No

    # input place holders
    Y = tf.compat.v1.placeholder(tf.float32, [None, feature_dim])
    Z = tf.compat.v1.placeholder(tf.float32, [None, feature_dim])
    M = tf.compat.v1.placeholder(tf.float32, [None, feature_dim])
    keep_prob = tf.compat.v1.placeholder(tf.float32)

    # build a FC network
    # For compatibility: had to change from xavier to tf.initializers.GlorotUniform()
    U = tf.compat.v1.get_variable("U", shape=[feature_dim, hidden_no], initializer=tf.initializers.GlorotUniform())
    V1 = tf.compat.v1.get_variable("V1", shape=[feature_dim, hidden_no], initializer=tf.initializers.GlorotUniform())
    V2 = tf.compat.v1.get_variable("V2", shape=[feature_dim, hidden_no], initializer=tf.initializers.GlorotUniform())
    b = tf.Variable(tf.compat.v1.random_normal([hidden_no]))

    L1 = tf.nn.sigmoid((tf.matmul(Y,tf.compat.v1.matrix_set_diag(U, np.zeros([feature_dim,]))) + tf.matmul(Z, tf.compat.v1.matrix_set_diag(V1, np.zeros([feature_dim,]))) + tf.matmul(M, V2) + b))
    L1D = tf.nn.dropout(L1, keep_prob)

    W = tf.Variable(tf.compat.v1.random_normal([feature_dim]))
    a = tf.Variable(tf.compat.v1.random_normal([feature_dim]))
    hypothesis = W * L1D + a

    outputs = tf.nn.sigmoid(hypothesis)

    # reshape out for sequence_loss
    loss = tf.sqrt(tf.reduce_mean(tf.square(M*outputs - M*Y)) )

    # Optimizer
    optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate)
    train = optimizer.minimize(loss)

    # Sessions
    sess = tf.compat.v1.Session()
    sess.run(tf.compat.v1.global_variables_initializer())

    # keep_prob_var = 1.0      # For the dropout, renamned to keep_prob_var. 1.0 means no dropout (which is default)
    # Training step
    for i in range(iterations):
        _, step_loss = sess.run([train, loss], feed_dict={Y: col_trainZ, Z: col_rec_trainZ, M: col_trainM, keep_prob: keep_prob_var})

        # Test step
    train_predict = sess.run(outputs, feed_dict={Y: col_trainZ, Z: col_rec_trainZ, M: col_trainM, keep_prob:keep_prob_var})
    test_predict = sess.run(outputs, feed_dict={Y: col_testZ, Z: col_rec_testZ, M: col_testM, keep_prob:keep_prob_var})

    output_train_temp = np.reshape(train_predict,[Train_No, Seq_No, feature_dim])
    output_test_temp = np.reshape(test_predict,[Test_No, Seq_No, feature_dim])

    #%%
    output_train = output_train_temp * (1-trainM) + trainZ * trainM
    output_test = output_test_temp * (1-testM) + testZ * testM


    #%% Initial point interpolation (Only for the performance)
    # If the first variable is missing, interpolate

    for i in range(len(trainZ[:,0,0])):
        for k in range(len(trainZ[0,0,:])):
            for j in range(len(trainZ[0,:,0])):
                if (trainT[i,j,k] > j):
                    idx = np.where(trainM[i,:,k]==1)[0]
                    if (np.size(idx) != 0):
                        final_results_train[i,j,k] = trainZ[i,np.min(idx),k]


    for i in range(len(testZ[:,0,0])):
        for k in range(len(testZ[0,0,:])):
            for j in range(len(testZ[0,:,0])):
                if (testT[i,j,k] > j):
                    idx = np.where(testM[i,:,k]==1)[0]
                    if (np.size(idx) != 0):
                        final_results_test[i,j,k] = testZ[i,np.min(idx),k]

    return [output_train, output_test]


#%%
