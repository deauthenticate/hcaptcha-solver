import tensorflow as tf, utilities, os

def LoadDataSet(path):
    vehicle_dataset = tf.keras.models.load_model(path)
    os.system('cls')
    return vehicle_dataset