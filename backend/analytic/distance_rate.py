from tensorflow.python import keras
from tensorflow.python.keras import optimizers
from tensorflow.python.keras import layers
from matplotlib import pyplot as plt
import random
import numpy as np
from typing import Optional
from keras.models import load_model as load_keras_model
import logging
import importlib

logging.basicConfig(encoding='utf-8', level=logging.INFO)


model: Optional[keras.Sequential] = None


# INPUTS: (count, min_dest, average_dest, nearest_modifier, average_modifier)

MODEL_PATH = 'analytic/data/distance_rate.model'
DATASET_PATH = 'analytic/data/distance_rate.py'
DATASET_MODULE = 'analytic.data.distance_rate'


def load_model():
    global model

    try:
        model = load_keras_model(MODEL_PATH)
    except:
        model = keras.Sequential()
        model.add(layers.Flatten(input_shape=(5, )))
        model.add(layers.Dense(4, activation='linear'))
        model.add(layers.Dense(3, activation='softmax'))
        model.add(layers.Dense(1, activation='linear'))
        model.compile(
            loss='mean_squared_error',
            optimizer=optimizers.adam_v2.Adam(0.005)
        )


def load_dataset() -> list:
    try:
        module = importlib.import_module(DATASET_MODULE)
        dataset = [module.inputs, module.outputs]
    except:
        dataset = [[], []]
    return dataset


def train():
    global model

    dataset = load_dataset()

    while True:
        count = random.randint(1, 9)
        x = np.random.randint(0, 500, count)
        y = np.random.random(count)

        plt.scatter(x, y)
        plt.grid()
        plt.show(block=False)

        try:
            resp = float(input("Result: "))
            nearest_y = max([
                y[j] for j in range(count)
                if j in [i for i in range(count) if x[i] == min(x)]
            ])

            dataset[0].append([count, min(x), x.mean(), nearest_y, y.mean()])
            dataset[1].append(resp)

            logging.info(str(dataset[0][-1]))
        except:
            break
        finally:
            plt.close()

    model.fit(dataset[0], dataset[1], epochs=20)
    model.save(MODEL_PATH)

    with open(DATASET_PATH, 'w') as file:
        file.write(f"inputs = {dataset[0]}\n")
        file.write(f"outputs = {dataset[1]}\n")


def predict(
        count: int,
        min_dest: float,
        average_dest: float,
        nearest_modifier: float,
        average_modifier: float
) -> float:
    if not model:
        load_model()

    return model.predict((count, min_dest, average_dest, nearest_modifier, average_modifier))[0][0]
