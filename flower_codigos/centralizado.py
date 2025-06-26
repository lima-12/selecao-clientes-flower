
from keras.models import Sequential
from keras.layers import Dense, Flatten, Dropout
from keras.datasets import mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train/255.0, x_test/255.0

modelo = Sequential()
modelo.add(Flatten(input_shape=(x_train.shape[1:])))
modelo.add(Dense(128, activation='relu'))
modelo.add(Dropout(0.1))
modelo.add(Dense(10, activation='softmax'))
modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['acc'])

modelo.fit(x_train, y_train, epochs=10)
loss, accuracy = modelo.evaluate(x_test, y_test)

print(f"Acurácia do modelo centralizado: {accuracy}")