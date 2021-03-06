# encoding=utf-8

import tensorflow as tf
from tensorflow.contrib import layers
from hyperparams import Hyperparams as params

learning_rate = params.learning_rate
threshold = params.threshold

col_num = params.col_num
L_layer1_num = params.L_layer1_num
L_layer2_num = params.L_layer2_num
L_layer3_num = params.L_layer3_num

row_num = params.row_num
R_layer1_num = params.R_layer1_num
R_layer2_num = params.R_layer2_num
R_layer3_num = params.R_layer3_num

keep_prob = params.keep_prob
reg = params.reg


class DMF(object):
    def __init__(self, use_side_info=False, feature_dim=5):
        with tf.name_scope('placeholder'):
            self.Y_input = tf.placeholder(tf.int32, [None, 1])
            self.XL_input = tf.placeholder(tf.float32, [None, col_num])
            self.XR_input = tf.placeholder(tf.float32, [None, row_num])
            self.U_input = tf.placeholder(tf.float32, [None, feature_dim])
            self.V_input = tf.placeholder(tf.float32, [None, feature_dim])
        with tf.variable_scope('DMF_net'):
            with tf.name_scope('L_net'):
                XL_emb1 = layers.fully_connected(self.XL_input, L_layer1_num,
                                                 activation_fn=tf.nn.relu,
                                                 weights_regularizer=layers.l2_regularizer(scale=reg),
                                                 weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 )
                XL_emb1 = tf.nn.dropout(XL_emb1, keep_prob=keep_prob)
                XL_emb2 = layers.fully_connected(XL_emb1, L_layer2_num,
                                                 activation_fn=tf.nn.relu,
                                                 weights_regularizer=layers.l2_regularizer(scale=reg),
                                                 weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 )
                XL_emb2 = tf.nn.dropout(XL_emb2, keep_prob=keep_prob)
                XL_emb3 = layers.fully_connected(XL_emb2, L_layer3_num,
                                                 activation_fn=tf.nn.relu,
                                                 weights_regularizer=layers.l2_regularizer(scale=reg),
                                                 weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 )
                XL_emb3 = tf.nn.dropout(XL_emb3, keep_prob=keep_prob)

            with tf.name_scope('R_net'):
                XR_emb1 = layers.fully_connected(self.XR_input, R_layer1_num,
                                                 activation_fn=tf.nn.relu,
                                                 weights_regularizer=layers.l2_regularizer(scale=reg),
                                                 weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 )
                XR_emb1 = tf.nn.dropout(XR_emb1, keep_prob=keep_prob)
                XR_emb2 = layers.fully_connected(XR_emb1, R_layer2_num,
                                                 activation_fn=tf.nn.relu,
                                                 weights_regularizer=layers.l2_regularizer(scale=reg),
                                                 weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 )
                XR_emb2 = tf.nn.dropout(XR_emb2, keep_prob=keep_prob)
                XR_emb3 = layers.fully_connected(XR_emb2, R_layer3_num,
                                                 activation_fn=tf.nn.relu,
                                                 weights_regularizer=layers.l2_regularizer(scale=reg),
                                                 weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                 )
                XR_emb3 = tf.nn.dropout(XR_emb3, keep_prob=keep_prob)


            if use_side_info:
                with tf.name_scope('SIDE_INFO_CONCAT'):
                    XL_emb3 = tf.concat([XL_emb3, self.U_input], axis=1)
                    XR_emb3 = tf.concat([XR_emb3, self.V_input], axis=1)

            with tf.name_scope('Latent_concate'):
                fuse_tensor = tf.multiply(XL_emb3, XR_emb3)

            with tf.name_scope('Output'):
                logits = layers.fully_connected(fuse_tensor, 1,
                                                weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                biases_initializer=tf.truncated_normal_initializer(stddev=0.1),
                                                activation_fn=None,
                                                weights_regularizer=layers.l2_regularizer(scale=reg))
        loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.cast(self.Y_input, tf.float32), logits=logits)
        with tf.name_scope('Train'):
            reg_ws = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES, 'DMF_net')
            self.score = tf.nn.sigmoid(logits)
            self.reg_loss = tf.reduce_mean(reg_ws)
            self.loss = tf.reduce_mean(loss) + self.reg_loss
            self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(self.loss)
            self.prediction = tf.cast(tf.greater_equal(self.score, threshold), tf.int32)
            self.accuracy = tf.reduce_mean(tf.cast(tf.equal(self.prediction, self.Y_input), tf.float32))


if __name__ == '__main__':
    print(DMF())
