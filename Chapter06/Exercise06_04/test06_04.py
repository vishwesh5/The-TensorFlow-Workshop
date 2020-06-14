import unittest
import import_ipynb
import pandas as pd
import numpy as np
import pandas.testing as pd_testing
import numpy.testing as np_testing
import tensorflow as tf
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
import kerastuner as kt


def model_builder(hp):
	model = tf.keras.Sequential()

	hp_units = hp.Int('units', min_value=128, max_value=512, step=64)

	reg_fc1 = Dense(hp_units, input_shape=(42,), activation='relu',
					kernel_regularizer=tf.keras.regularizers.l2(l=0.0001))
	reg_fc2 = Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l=0.0001))
	reg_fc3 = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l=0.0001))
	reg_fc4 = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l=0.0001))
	reg_fc5 = Dense(3, activation='softmax')

	model.add(reg_fc1)
	model.add(reg_fc2)
	model.add(reg_fc3)
	model.add(reg_fc4)
	model.add(reg_fc5)

	loss = tf.keras.losses.SparseCategoricalCrossentropy()
	hp_learning_rate = hp.Choice('learning_rate', values=[0.01, 0.001, 0.0001])

	optimizer = tf.keras.optimizers.Adam(hp_learning_rate)
	model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

	return model


class Test(unittest.TestCase):
	def setUp(self):
		import Exercise06_04
		self.exercises = Exercise06_04

		self.file_url = 'https://raw.githubusercontent.com/PacktWorkshops/The-TensorFlow-Workshop/master/Chapter06/dataset/connect-4.csv'

		self.data = pd.read_csv(self.file_url)
		self.target = self.data.pop('class')

		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.data, self.target, test_size=0.2, random_state=42)

		np.random.seed(8)
		tf.random.set_seed(8)

		tuner = kt.Hyperband(model_builder, objective = 'val_accuracy', max_epochs = 5)
		tuner.search(self.X_train, self.y_train, validation_data=(self.X_test, self.y_test))
		best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
		self.best_units = best_hps.get('units')
		self.best_lr = best_hps.get('learning_rate')
		self.model = tuner.hypermodel.build(best_hps)

	def test_file_url(self):
		self.assertEqual(self.exercises.file_url, self.file_url)

	def test_data(self):
		pd_testing.assert_frame_equal(self.exercises.data, self.data)

	def test_target(self):
		np_testing.assert_array_equal(self.exercises.target, self.target)

	def test_X_train(self):
		pd_testing.assert_frame_equal(self.exercises.X_train, self.X_train)

	def test_y_train(self):
		np_testing.assert_array_equal(self.exercises.y_train, self.y_train)

	def test_X_test(self):
		pd_testing.assert_frame_equal(self.exercises.X_test, self.X_test)

	def test_y_test(self):
		np_testing.assert_array_equal(self.exercises.y_test, self.y_test)

	def test_best_units(self):
		self.assertEqual(self.exercises.best_units, self.best_units)

	def test_best_lr(self):
		self.assertEqual(self.exercises.best_lr, self.best_lr)

	def test_summary(self):
		self.assertEqual(self.exercises.model.summary(), self.model.summary())


if __name__ == '__main__':
	unittest.main()
