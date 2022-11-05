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

NORMALIZATION_COUNT = 100
NORMALIZATION_DISTANCE = 1000


def load_model():
    global model

    try:
        model = load_keras_model(MODEL_PATH)
    except:
        model = keras.Sequential()
        model.add(layers.Flatten(input_shape=(5, )))
        model.add(layers.Dense(4, activation='softmax'))
        model.add(layers.Dropout(0.2))
        # model.add(layers.Dense(3, activation='softmax'))
        model.add(layers.Dense(1, activation='linear'))
        model.compile(
            loss='mean_squared_error',
            optimizer=optimizers.adam_v2.Adam(0.001)
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

    fig, ax = plt.subplots()

    while True:
        count = random.randint(1, 20)
        x = np.random.randint(0, 1000, count)
        y = np.random.random(count)

        ax.scatter(x, y)
        ax.grid()
        fig.set_figwidth(20)
        fig.set_figheight(20)

        plt.show(block=False)

        nearest_y = max([
            y[j] for j in range(count)
            if j in [i for i in range(count) if x[i] == min(x)]
        ])

        logging.info(str([count, min(x), x.mean(), nearest_y, y.mean()]))
        try:
            resp = float(input("Result: "))


            dataset[0].append([count, min(x), x.mean(), nearest_y, y.mean()])
            dataset[1].append(resp)


        except:
            plt.close()
            break
        finally:
            ax.clear()

    model.fit(
        [(
            x[0] / NORMALIZATION_COUNT,
            x[1] / NORMALIZATION_DISTANCE,
            x[2] / NORMALIZATION_DISTANCE,
            x[3],
            x[4]
        ) for x in dataset[0]],
        dataset[1],
        epochs=150
    )
    model.save(MODEL_PATH)

    with open(DATASET_PATH, 'w') as file:
        file.write(f"inputs = {dataset[0]}\n")
        file.write(f"outputs = {dataset[1]}\n")

    while True:
        count = random.randint(1, 9)
        x = np.random.randint(0, 500, count)
        y = np.random.random(count)

        nearest_y = max([
            y[j] for j in range(count)
            if j in [i for i in range(count) if x[i] == min(x)]
        ])

        try:
            resp = predict(count, min(x), x.mean(), nearest_y, y.mean())
            logging.info(str([count, min(x), x.mean(), nearest_y, y.mean()]) + "\n" + str(resp))
            input()
        except:
            plt.close()
            break
        finally:
            ax.clear()


def predict(
        count: int,
        min_dest: float,
        average_dest: float,
        nearest_modifier: float,
        average_modifier: float
) -> float:
    global model

    if not model:
        load_model()

    if not count:
        return 0

    return model.predict([(
        count / NORMALIZATION_COUNT,
        min_dest / NORMALIZATION_DISTANCE,
        average_dest / NORMALIZATION_DISTANCE,
        nearest_modifier,
        average_modifier
    )])[0][0]
