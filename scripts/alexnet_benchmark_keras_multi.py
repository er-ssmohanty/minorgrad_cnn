# -*- coding: utf-8 -*-
"""Alexnet_Benchmark_Keras_Multi.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MY2nxsa1iayuF5ABc0ff-Iw9-fpgd150
"""

import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout, BatchNormalization, Activation
#import tensorflow.keras.applications as apps

class MyModel(Model):
  def __init__(self):
    super(MyModel, self).__init__()
    self.convinp = Conv2D(filters=96, input_shape=(227, 227,1), kernel_size=(11,11), strides=(4,4), padding='same', activation='relu')
    self.mxpl_1 = MaxPooling2D(pool_size=(3,3), strides=(2,2), padding='same')
    self.conv256_1 = Conv2D(filters=256, kernel_size=(5,5), strides=(1,1), padding='same', activation='relu')
    self.mxpl_2 = MaxPooling2D(pool_size=(3,3), strides=(2,2), padding='same')
    self.conv384_1 = Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), padding='same', activation='relu')
    self.conv384_2 = Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), padding='same', activation='relu')
    self.conv256_2 = Conv2D(filters=256, kernel_size=(5,5), strides=(1,1), padding='same', activation='relu')
    self.mxpl_3 = MaxPooling2D(pool_size=(3,3), strides=(2,2), padding='same')
    self.flatten = Flatten()
    self.dense4K_1 = Dense(4096, activation='relu')
    self.drop_1=Dropout(0.4)
    self.dense4K_2 = Dense(4096, activation='relu')
    self.drop_2=Dropout(0.4)
    self.dense1K = Dense(1000, activation='relu')
    self.drop_3=Dropout(0.4)
    self.denseop = Dense(3, activation='softmax') 

  def call(self, x):
    x = self.convinp(x)
    x = self.mxpl_1(x)
    x = self.conv256_1(x)
    x = self.mxpl_2(x)
    x = self.conv384_1(x)
    x = self.conv384_2(x)
    x = self.conv256_2(x)
    x = self.mxpl_3(x)
    x = self.flatten(x)
    x = self.dense4K_1(x)
    x = self.drop_1(x)
    x = self.dense4K_2(x)
    x = self.drop_2(x)
    x = self.dense1K(x)
    x = self.drop_3(x)
    return self.denseop(x)
# Create an instance of the model
model = MyModel()

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),\
              loss=tf.keras.losses.MSE,\
              metrics=tf.keras.metrics.Accuracy())

train_dir="/content/drive/MyDrive/cbis_ddsm/mass/train"
test_dir="/content/drive/MyDrive/cbis_ddsm/mass/test"
train_data = tf.keras.preprocessing.image_dataset_from_directory(train_dir, color_mode="grayscale",image_size=(227,227), batch_size=10)
# test_data = tf.keras.preprocessing.image_dataset_from_directory(test_dir, color_mode="grayscale",image_size=(227,227), batch_size=10)

model.fit(train_data,epochs=10)



loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
# loss_object = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
optimizer = tf.keras.optimizers.Adam()

# train_loss = tf.keras.metrics.Mean(name='train_loss')
train_loss = tf.keras.metrics.FalsePositives(name='train_loss')
# train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')
train_accuracy = tf.keras.metrics.Recall(name='train_accuracy')

test_loss = tf.keras.metrics.Mean(name='test_loss')
test_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='test_accuracy')

@tf.function
def train_step(images, labels):
  with tf.GradientTape() as tape:
    # training=True is only needed if there are layers with different
    # behavior during training versus inference (e.g. Dropout).
    predictions = model(images, training=True)
    loss = loss_object(labels, predictions)
  gradients = tape.gradient(loss, model.trainable_variables)
  optimizer.apply_gradients(zip(gradients, model.trainable_variables))

  train_loss(loss)
  train_accuracy(labels, predictions)

@tf.function
def test_step(images, labels):
  # training=False is only needed if there are layers with different
  # behavior during training versus inference (e.g. Dropout).
  predictions = model(images, training=False)
  t_loss = loss_object(labels, predictions)

  test_loss(t_loss)
  test_accuracy(labels, predictions)

import sys

EPOCHS = 5

for epoch in range(EPOCHS):
  # Reset the metrics at the start of the next epoch
  train_loss.reset_states()
  train_accuracy.reset_states()
  # test_loss.reset_states()
  # test_accuracy.reset_states()
  sys.stdout.write("|")
  for images, labels in train_data:
    sys.stdout.write("=")
    #labels2=tf.keras.utils.to_categorical(labels,3)
    train_step(images, labels)

  # for test_images, test_labels in test_ds:
  #   test_step(test_images, test_labels)
  print()
  print(
    f'Epoch {epoch + 1}, '
    f'Loss: {train_loss.result()}, '
    f'Accuracy: {train_accuracy.result() * 100}, '
  #   f'Test Loss: {test_loss.result()}, '
  #   f'Test Accuracy: {test_accuracy.result() * 100}'
  )

tf.keras.utils.plot_model(model, to_file='model.png', show_shapes=True, show_dtype=True, show_layer_names=True, rankdir='TB', expand_nested=True, dpi=96, layer_range=None, show_layer_activations=True)

model.summary()