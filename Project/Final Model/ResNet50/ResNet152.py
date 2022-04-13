# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 02:05:39 2022

@author: psingh24
"""

# Importing libraries
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Model, load_model
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.resnet50 import ResNet50
# from tensorflow.keras.applications.resnet import ResNet101
from tensorflow.keras.applications.resnet import ResNet152

from tensorflow.keras.preprocessing.image import ImageDataGenerator

from sklearn import metrics
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Re-sizing all images
Img_size = [224, 224]

train_path = 'Train\*'
test_path = 'Test'

resnet = ResNet152(input_shape = Img_size + [3], weights = 'imagenet', include_top = False)

# using the pre-trained weights initially and updating them during the training phase
for layer in resnet.layers:
    layer.trainable = True
    
folders = glob(train_path)

x = Flatten()(resnet.output)

prediction = Dense(len(folders), activation = 'softmax')(x)

model = Model(inputs = resnet.input, outputs = prediction)

# print(model.summary())

model.compile(loss = 'categorical_crossentropy', optimizer = tf.keras.optimizers.Adam(), metrics  = ['accuracy'])

# Data Augmentation
train_datagen = ImageDataGenerator(rescale = 1./255, shear_range = 0.2, zoom_range = 0.2, horizontal_flip = True)
test_datagen = ImageDataGenerator(rescale = 1./255)

training_set = train_datagen.flow_from_directory('Train', target_size = (224,224), batch_size = 32, class_mode = 'categorical')
test_set = test_datagen.flow_from_directory('Test', target_size = (224,224), batch_size = 32, class_mode = 'categorical')

checkpointer = tf.keras.callbacks.ModelCheckpoint('WeedDetectionModelR50.h5', save_best_only = True, verbose = 1)

callbacks = [
    tf.keras.callbacks.TensorBoard(log_dir = 'logs'),
    tf.keras.callbacks.EarlyStopping(patience = 5, monitor = 'val_loss'),
    checkpointer]

result = model.fit(training_set, validation_data = test_set, epochs = 100, 
                             steps_per_epoch = len(training_set), validation_steps = len(test_set), callbacks = callbacks)

# plot the loss
plt.plot(result.history['loss'], label='train loss')
plt.plot(result.history['val_loss'], label='val loss')
plt.legend()
plt.xlabel('Epochs')
plt.ylabel('Categorical crossentropy Error')
plt.xticks([x for x in range(0,10)])
plt.title('Training Vs Validation loss')
plt.savefig('LossVal_lossR101FineTune')
plt.show()

# plot the accuracy
plt.plot(result.history['accuracy'], label='train acc')
plt.plot(result.history['val_accuracy'], label='val acc')
plt.xticks([x for x in range(0,10)])
plt.xlabel('Epochs')
plt.ylabel('Accuracy values')
plt.title('Training Vs validation accuracy')
plt.legend()
plt.savefig('AccVal_accR1010.FineTune')
plt.show()

y_pred = model.predict(test_set)
print(y_pred)

y_pred = np.argmax(y_pred, axis=1)
print(y_pred)

# Method to calculate the confusion matrix
testing = []
for i in range(len(test_set)):
    testing.append(list(np.argmax(test_set[i][1], axis=1)))

actual = []
for i in range(len(testing)):
    for j in testing[i]:
        actual.append(j)
actual = np.array(actual)

confusion_matrix = metrics.confusion_matrix(actual, y_pred)
confusion_matrix = confusion_matrix/1527

print(metrics.classification_report(actual, y_pred))

sns.heatmap(confusion_matrix, annot = True, cmap = 'BuPu')
