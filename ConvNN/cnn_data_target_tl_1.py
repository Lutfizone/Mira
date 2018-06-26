# import tflearn
import pickle
import numpy as np
import tensorflow as tf
# from tflearn.data_utils import shuffle

from sklearn import metrics

from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten
from keras.layers.convolutional import Conv1D
from keras.layers import MaxPooling1D
from keras.optimizers import Adam, Adamax
from keras.models import load_model
from keras.initializers import glorot_normal
from keras.callbacks import ModelCheckpoint, EarlyStopping

model_source = '../Checkpoints/intervene.data-source.h5'
model_target = "../Checkpoints/intervene.data-target-wtl-retrain.h5"

data_path = "../data/splitted/data_target/"

X = np.load(data_path + "X.npy")
Y = np.load(data_path + "Y.npy")
X_test = np.load(data_path + "X_test.npy")
Y_test = np.load(data_path + "Y_test.npy")

X = np.expand_dims(X, axis=2)
X_test = np.expand_dims(X_test, axis=2)

checkpoint_path = '../Checkpoints/intervene.data-target-tl.h5'
early_stopper = EarlyStopping(monitor='loss', patience=10, verbose=0, mode='auto')
checkpointer = ModelCheckpoint(filepath=checkpoint_path, verbose=1, save_best_only=True)

trained_model = load_model(model_source)
trained_model_target = load_model(model_target)
print trained_model.summary()

model = Sequential()
for layer in trained_model.layers[:1]:
	model.add(layer)
model.add(Flatten())
model.add(Dropout(0.1))
model.add(Dense(180, activation='sigmoid'))
model.add(Dropout(0.5))
model.add(Dense(len(Y[0]), activation='softmax'))

# for layer in model.layers[:1]:
#     layer.trainable = False
# model.layers[5].trainable = False

print model.summary()

model.compile(loss='binary_crossentropy',
              optimizer=Adam(lr=0.001, decay=1e-8),
              metrics=['accuracy'])

# Fit the model
model.fit(X, Y,
          batch_size=32,
          shuffle=True,
          epochs=2000,
          validation_data=(X_test, Y_test),
          callbacks=[checkpointer, early_stopper])

# load best model
model = load_model(checkpoint_path)

predictions = model.predict(X_test)
predictions = [np.argmax(predictions[i]) for i in range(len(predictions))]
predictions = np.array(predictions)
labels = [np.argmax(Y_test[i]) for i in range(len(Y_test))]
labels = np.array(labels)

print predictions
print labels

print "Accuracy: " + str(100*metrics.accuracy_score(labels, predictions))
print "Precision: " + str(100*metrics.precision_score(labels, predictions, average="weighted"))
print "Recall: " + str(100*metrics.recall_score(labels, predictions, average="weighted"))
print "f1_score: " + str(100*metrics.f1_score(labels, predictions, average="weighted"))

print model.summary()
print model.evaluate(X_test, Y_test, batch_size=32)
