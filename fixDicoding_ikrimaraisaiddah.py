# -*- coding: utf-8 -*-
"""FixProyekKlasifiksiGambar_ IkrimaRaiSaiddah.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X8HYjsWz6tNlaZfWjWFXrUTecEP8heE8

# Proyek Klasifikasi Gambar:puneet6060/intel-image-classification

* Nama: ikrima Rai Saiddah
* Email: ikrimarai13@gmail.com
* ID Dicoding: ikrimars

## Import Semua Packages/Library yang Digunakan
"""

# Library yang sering digunakan
import os, shutil
import zipfile
import random
from random import sample
from shutil import copyfile
import pathlib
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm.notebook import tqdm as tq

# Libraries untuk pemrosesan data gambar
import cv2
from PIL import Image
import skimage
from skimage import io
from skimage.transform import resize
from skimage.transform import rotate, AffineTransform, warp
from skimage import img_as_ubyte
from skimage.exposure import adjust_gamma
from skimage.util import random_noise

!pip install --upgrade tensorflow
!pip install tensorflowjs
!pip install tensorflow

# Libraries untuk pembangunan model
import keras
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf
import tensorflowjs as tfjs
# from tensorflow.keras import layers, models, optimizers, regularizers
from tensorflow.keras import Model, layers, optimizers, regularizers, models
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from tensorflow.keras.optimizers import Adam, RMSprop, SGD
from tensorflow.keras.layers import InputLayer, Conv2D, SeparableConv2D, MaxPooling2D, MaxPool2D, Dense, Flatten, Dropout, BatchNormalization
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.applications import MobileNet
# from tensorflow.keras.applications.densenet import DenseNet121
# from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint, Callback, EarlyStopping, ReduceLROnPlateau

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Mencetak versiyang sedang digunakan
print(f"{'Tensorflow Version':25}: {tf.__version__}")
print(f"{'TensorflowJS Version':25}: {tfjs.__version__}")
print(f"{'Matplotlib Version':25}: {matplotlib.__version__}")
print(f"{'Scikit-Learn Version':25}: {sklearn.__version__}")
print(f"{'Numpy Version':25}: {np.__version__}")
print(f"{'Pandas Version':25}: {pd.__version__}")

"""## Data Preparation

### Data Loading

**Mengambil data dari kagle**
"""

# Import module yang disediakan google colab untuk kebutuhan upload file

from google.colab import files
files.upload()

# Download kaggle dataset and unzip the file
# !cp kaggle.json ~/.kaggle/

# !chmod 600 ~/.kaggle/kaggle.json
!kaggle datasets download -d puneet6060/intel-image-classification
!unzip intel-image-classification.zip

"""### Data Preprocessing"""

# Direktori awal untuk train dan test
train_dir = "seg_test/seg_test"
test_dir = "seg_train/seg_train"

# Direktori baru untuk dataset gabungan
dir = "imageClassification/dataset"

# Buat direktori baru untuk dataset gabungan
os.makedirs(dir, exist_ok=True)

# Salin file dan folder dari train
for category in os.listdir(train_dir):
    category_dir = os.path.join(train_dir, category)
    if os.path.isdir(category_dir):
        shutil.copytree(category_dir, os.path.join(dir, category), dirs_exist_ok=True)

# Salin file dan folder dari test
for category in os.listdir(test_dir):
    category_dir = os.path.join(test_dir, category)
    if os.path.isdir(category_dir):
        shutil.copytree(category_dir, os.path.join(dir, category), dirs_exist_ok=True)

# format gambar yang diizinkan
formatted= ['.png', '.jpg', '.jpeg']

# list untuk label dan path
labels = []
path = []
# Dapatkan nama file gambar, path file, dan label satu per satu dengan looping, dan simpan sebagai dataframe
for dirname, _, filenames in os.walk(dir):
    for filename in filenames:
        # format gambar pada file
        if os.path.splitext(filename)[-1].lower() in formatted:
            labels.append(os.path.split(dirname)[-1])
            path.append(os.path.join(dirname, filename))

# membuat dataframe
df = pd.DataFrame(columns=['path','labels'])
df['path']=path
df['labels']=labels
df.head()

df.info()

#melihatkan informasi isi data
df['labels'].value_counts()

#melihatkan data label
df['labels'].unique()

"""Dataset intel image clasification terdapat 17024 dataset dgn type object/gambar.
Dataset ini memiliki 6 label diantaranya: 'buildings', 'mountain', 'glacier', 'street', 'sea', 'forest'. Dengan informasi jumlah data sebagai berikut:
* mountain	3037
* glacier	2957
* street	2883
* sea	2784
* forest	2745
* buildings	2628

#### Mengambil sampel gambar
"""

# Ambil daftar kategori unik
kategori_unik = df['labels'].unique()

# Atur ukuran plot
plt.figure(figsize=(15, 12))

# Loop untuk menampilkan satu gambar dari setiap kategori unik
for indeks, kategori in enumerate(kategori_unik):
    plt.subplot(3, 3, indeks + 1)  # Buat subplot (3 baris, 3 kolom)

    # Ambil path gambar pertama dari kategori saat ini
    path_gambar = df[df['labels'] == kategori].iloc[0, 0]

    # Baca dan tampilkan gambar
    gambar = plt.imread(path_gambar)
    plt.imshow(gambar)
    plt.title(kategori)  # Tambahkan judul dengan nama kategori
    plt.title(kategori, pad= 20)

    # Atur skala sumbu x dan y berdasarkan ukuran gambar
    tinggi, lebar = gambar.shape[:2]
    plt.xticks([0, lebar // 2, lebar], [0, lebar // 2, lebar])
    plt.yticks([0, tinggi // 2, tinggi], [0, tinggi // 2, tinggi])

    plt.xlabel('Lebar (Width)', labelpad=10)
    plt.ylabel('Tinggi (Height)', labelpad=10)
    plt.axis('on')  # Tampilkan sumbu koordinat

# Tata letak agar tidak saling tumpang tindih
plt.tight_layout()

# Tampilkan hasilnya
plt.show()

import seaborn as sns
distribution_train = pd.DataFrame({"path":path, 'file_name':dirname, "labels":labels})


# Plot distribusi gambar di setiap kelas
Label = distribution_train['labels']
plt.figure(figsize = (6,6))
sns.set_style("darkgrid")
plot_data = sns.countplot(Label)

"""Berdasarkan hasil grafik distribusi data terdapat jumlah data yang tertinggi yaitu mountain dan yang terendah yaitu buildings. Namun, secara keseluruhan tidak ada imbalance data sekitar 2500-3000 data.

#### Split Dataset
"""

# Contoh dataframe (df) harus berisi kolom ['image_path', 'label']
# df = pd.read_csv("path_to_csv")  # Jika datamu berasal dari CSV

# Membagi dataset menjadi training (80%) dan testing (20%)
train_df, test_df = train_test_split(df,
                                     test_size=0.2,
                                     shuffle=True,
                                     random_state=42)

# Cek jumlah data setelah split
print("Jumlah data training:", train_df.shape[0])
print("Jumlah data testing :", test_df.shape[0])

# Tambahkan kolom 'set' untuk menandai apakah data itu Training atau Testing
train_df['set'] = 'Train'
test_df['set'] = 'Test'

# Gabungkan kembali untuk analisis distribusi data
df_all = pd.concat([train_df, test_df], ignore_index=True)

# Tampilkan jumlah data per kategori untuk setiap set
print('===================================================== \n')
print(df_all.groupby(['set', 'labels']).size(), '\n')
print('===================================================== \n')

# Tampilkan 5 sampel acak dari dataset gabungan
print(df_all.sample(5))

# # Path dataset asli & dataset hasil pembagian
datasource_path = "imageClassification/dataset/"  # Dataset asli
dataset_path = "datasetFinal/"  # Dataset setelah pembagian train-test

# Check shape of df
print(train_df.shape)
print(test_df.shape)

for index, row in tq(df_all.iterrows()):
    # Deteksi filepath
    file_path = row['path']
    if os.path.exists(file_path) == False:
            file_path = os.path.join(datasource_path,row['labels'],row['image'].split('.')[0])

    # Buat direktori tujuan folder
    if os.path.exists(os.path.join(dataset_path,row['set'],row['labels'])) == False:
        os.makedirs(os.path.join(dataset_path,row['set'],row['labels']))

    # Tentukan tujuan file
    destination_file_name = file_path.split('/')[-1]
    file_dest = os.path.join(dataset_path,row['set'],row['labels'],destination_file_name)

    # Salin file dari sumber ke tujuan
    if os.path.exists(file_dest) == False:
        shutil.copy2(file_path,file_dest)

# Definisikan direktori training dan test
TRAIN_DIR = "datasetFinal/Train/"
TEST_DIR = "datasetFinal/Test/"

train_buildings = os.path.join(TRAIN_DIR + '/buildings')
train_forest = os.path.join(TRAIN_DIR + '/forest')
train_glacier = os.path.join(TRAIN_DIR + '/glacier')
train_mountain = os.path.join(TRAIN_DIR + '/mountain')
train_sea = os.path.join(TRAIN_DIR + '/sea')
train_street = os.path.join(TRAIN_DIR + '/street')
test_buildings = os.path.join(TEST_DIR + '/buildings')
test_forest = os.path.join(TEST_DIR + '/forest')
test_glacier = os.path.join(TEST_DIR + '/glacier')
test_mountain = os.path.join(TEST_DIR + '/mountain')
test_sea = os.path.join(TEST_DIR + '/sea')
test_street = os.path.join(TEST_DIR + '/street')

print("Total number of buildings images in training set: ",len(os.listdir(train_buildings)))
print("Total number of forest images in training set: ",len(os.listdir(train_forest)))
print("Total number of glcier images in training set: ",len(os.listdir(train_glacier)))
print("Total number of mountain images in training set: ",len(os.listdir(train_mountain)))
print("Total number of sea images in training set: ",len(os.listdir(train_sea)))
print("Total number of street images in training set: ",len(os.listdir(train_street)))
print("Total number of buildings images in test set: ",len(os.listdir(test_buildings)))
print("Total number of forest images in test set: ",len(os.listdir(test_forest)))
print("Total number of glcier images in test set: ",len(os.listdir(test_glacier)))
print("Total number of mountain images in test set: ",len(os.listdir(test_mountain)))
print("Total number of sea images in test set: ",len(os.listdir(test_sea)))
print("Total number of street images in test set: ",len(os.listdir(test_street)))

"""Dataset intel image clasification, setelah dilakukan split data set sebesar 20% data test dan 80% data trai menghasilkan Jumlah data training: 13627 dan
Jumlah data testing : 3407. Dimana memiliki informasi detail data sebagai berikut:
> Data training:
* buildings images in training set:  2113
* forest images in training set:  2197
* glcier images in training set:  2368
* mountain images in training set:  2425
* sea images in training set:  2232
* street images in training set:  2292

> Data testing:
* buildings images in test set:  515
* forest images in test set:  548
* glcier images in test set:  589
* mountain images in test set:  612
* number of sea images in test set:  552
* street images in test set:  591

## Modelling
"""

# preprocessing data
# Definisikan fungsi callback
def resize_image(img):
    img = cv2.resize(img, (150, 150))
    return img

# Data Augmentation (Meningkatkan Variasi Data, akurasi, generalisasi)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    validation_split=0.2,
    preprocessing_function=resize_image
)

validation_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
test_datagen = ImageDataGenerator(rescale=1./255)

# Data Generators
train_generator = train_datagen.flow_from_directory(TRAIN_DIR,
                                                    target_size=(150, 150),
                                                    batch_size=32,
                                                    class_mode='categorical',
                                                    subset='training',
                                                    shuffle=True)

validation_generator = validation_datagen.flow_from_directory(TRAIN_DIR,
                                                              target_size=(150, 150),
                                                              batch_size=32,
                                                              class_mode='categorical',
                                                              subset='validation',
                                                              shuffle=False)

test_generator = test_datagen.flow_from_directory(TEST_DIR,
                                                  target_size=(150, 150),
                                                  batch_size=1,
                                                  class_mode='categorical',
                                                  shuffle=False)

"""Setelah itu dilakukan preprocessing data dimana

* train(pelatihan) memiliki  total 10.904 gambar dalam dataset yang terbagi ke dalam 6 kelas. Dalam tahap ini digunakan Data Augmentation (Meningkatkan Variasi Data, akurasi, generalisasi) dan juga dilakukan fungsi callback untuk menyamakan ukuran data gambar.

* validation (validasi) sebanyak
2.723 gambar, juga dalam 6 kelas.

* test (pengujian),sebanyak 3.407 gambar dalam 6 kelas.

### Pembangunan Model Parameter Tunning
"""

# Pembangunan Model Parameter Tunning
# Load Pretrained MobileNetV2
base_model = tf.keras.applications.MobileNetV2(input_shape=(150, 150, 3), include_top=False, weights='imagenet')
base_model.trainable = True  # Unfreeze layer terakhir

# Unfreeze hanya beberapa layer terakhir agar tidak overfit
for layer in base_model.layers[:-20]:
    layer.trainable = False

# Model Architecture
model = models.Sequential([
    base_model,
    layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.Dropout(0.4),
    layers.Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(6, activation='softmax')
])
# Display the model summary
model.summary()

# Compile Model
optimizer = optimizers.Adam(learning_rate=0.0005)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# Callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-6)

# Train Model
history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=25,
    callbacks=[early_stopping, reduce_lr]
)

results = model.evaluate(validation_generator, verbose=0)
print("Test Loss: {:.5f}".format(results[0]))
print("Test Accuracy: {:.2f}%".format(results[1] * 100))

results = model.evaluate(test_generator, verbose=0)
print("Test Loss: {:.5f}".format(results[0]))
print("Test Accuracy: {:.2f}%".format(results[1] * 100))

"""**Hasilnya,**

setelah beberapa percobaan di dapatkan model mencapai nilai:
* akurasi Train sebesar 92.47% dan loss 0.32826
* akurasi Test sebesar 92.22% dan loss 0.30868

Digunakan model dengan menggunakan transfer learning MobileNetV2 dikarenakan data yang digunakan memiliki banyak data sehingga diperlukan model yang sudah dilatih agar hasil lebih baik dibanding pelatihan secara manual.

MobileNet V2 yang digunakan dilakukan fine-tuning untuk melatih layers model di dalamnya agar tidak terjadi overfitting dan mempertahankan akurasi yang baik.

**Saran**

* melakukan perbandingan dengan optimizers lainnya.
* melakukan percobaan berbagai augmentasi yang cocok untuk dataset.
* melakukan percobaan Model Architecture dan transfer learning lain.

### Evaluasi dan visualisasi
"""

# grafik tanpa drop out 0.2
import matplotlib.pyplot as plt

# Mengambil data akurasi dan loss dari history training
acc_2 = history.history['accuracy']
val_acc_2 = history.history['val_accuracy']
loss_2 = history.history['loss']
val_loss_2 = history.history['val_loss']

epochs_2 = range(len(acc_2))

# Plot Akurasi
plt.figure(figsize=(10, 5))
plt.plot(epochs_2, acc_2, 'r', label='Training Accuracy')
plt.plot(epochs_2, val_acc_2, 'b', label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')
plt.grid()
plt.show()

# Plot Loss
plt.figure(figsize=(10, 5))
plt.plot(epochs_2, loss_2, 'r', label='Training Loss')
plt.plot(epochs_2, val_loss_2, 'b', label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend(loc='upper left')
plt.grid()
plt.show()

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

# Reset test generator sebelum prediksi
test_generator.reset()

# Melakukan prediksi menggunakan model
predict = model.predict(test_generator, verbose=0)

# Mengambil kelas dengan probabilitas tertinggi
preds_labels = np.argmax(predict, axis=1)

# Definisi label kelas
class_labels = ['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']

# Membuat Confusion Matrix
cm = confusion_matrix(test_generator.classes, preds_labels)

# Konversi ke DataFrame agar lebih mudah dibaca
cm_df = pd.DataFrame(cm, index=[f"Actual {cls}" for cls in class_labels],
                     columns=[f"Predicted {cls}" for cls in class_labels])

# Plot Confusion Matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", linewidths=0.5)
plt.title("Confusion Matrix")
plt.ylabel("Actual Labels")
plt.xlabel("Predicted Labels")
plt.show()

# Print Classification Report
print("\nClassification Report:\n")
print(classification_report(y_true=test_generator.classes,
                            y_pred=preds_labels,
                            target_names=class_labels, digits=4))

"""Model memiliki akurasi test sebesar 0.9222 (92.22%) dari total 3.407 gambar dengan benar.

Performa tidak merata antar kelas, pada "street" dan "Glacier" memiliki skor lebih rendah, mungkin karena kesamaan visual dengan kelas lain seperti street dan Mountain untuk kelas yang lebih sulit.
"""

model.save("classification_modelTFL.h5")

"""## Konversi Model

### Convert TFServing
"""

# Simpan model dalam format SavedModel
tf.saved_model.save(model, 'saved_model_dir')

"""### Convert TFJS"""

import tensorflowjs as tfjs

# os.makedirs(BaseDir+'tfjs_model', exist_ok=True)
tfjs.converters.save_keras_model(model, 'tfjs_model')

"""### Convert TFLite"""

# Convert the model to TF-Lite format
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TF-Lite model to a specific folder
os.makedirs('tf_lite', exist_ok=True)
# folder_path = 'tf_lite'
# file_path = f'{folder_path}/model.tflite'
file_path = f'tf_lite/model.tflite'
with open(file_path, 'wb') as f:
    f.write(tflite_model)

def recreate_labels():
    # labels = [folder for folder in os.listdir(dir) if not folder.startswith('.')]
    labels = ['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']
    with open('tf_lite/labels.txt', 'w') as file:
        for label in labels:
            file.write(label)
            file.write('\n')

recreate_labels()

"""## Inference

class_labels = ['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']

{'buildings' -> 0,
'forest' -> 1,
'glacier' -> 2,
'mountain' -> 3,
'sea' -> 4,
'street' -> 5 }

### Model.h5
"""

from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
modelan = load_model("classification_modelTFL.h5")

# Baca gambar baru
# img_path = "path/to/new/image.jpg"
img_path = "seg_test/seg_test/buildings/20057.jpg" #buildings

img = cv2.imread(img_path)
img = cv2.resize(img, (150, 150))
img = np.expand_dims(img, axis=0)  # Tambahkan batch dimension
img = img / 255.0  # Normalisasi

# Prediksi
pred = modelan.predict(img)
print("Prediksi kelas:", np.argmax(pred))

from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
modelan = load_model("classification_modelTFL.h5")

# Baca gambar baru
# img_path = "path/to/new/image.jpg"
img_path = "seg_test/seg_test/forest/20056.jpg" #forest

img = cv2.imread(img_path)
img = cv2.resize(img, (150, 150))
img = np.expand_dims(img, axis=0)  # Tambahkan batch dimension
img = img / 255.0  # Normalisasi

# Prediksi
pred = modelan.predict(img)
print("Prediksi kelas:", np.argmax(pred))

from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
modelan = load_model("classification_modelTFL.h5")

# Baca gambar baru
# img_path = "path/to/new/image.jpg"
img_path = "seg_test/seg_test/glacier/20059.jpg" #glacier

img = cv2.imread(img_path)
img = cv2.resize(img, (150, 150))
img = np.expand_dims(img, axis=0)  # Tambahkan batch dimension
img = img / 255.0  # Normalisasi

# Prediksi
pred = modelan.predict(img)
print("Prediksi kelas:", np.argmax(pred))

from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
modelan = load_model("classification_modelTFL.h5")

# Baca gambar baru
# img_path = "path/to/new/image.jpg"
img_path = "seg_test/seg_test/mountain/20058.jpg" #mountain

img = cv2.imread(img_path)
img = cv2.resize(img, (150, 150))
img = np.expand_dims(img, axis=0)  # Tambahkan batch dimension
img = img / 255.0  # Normalisasi

# Prediksi
pred = modelan.predict(img)
print("Prediksi kelas:", np.argmax(pred))

from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
modelan = load_model("classification_modelTFL.h5")

# Baca gambar baru
# img_path = "path/to/new/image.jpg"
img_path = "seg_test/seg_test/sea/20072.jpg" #sea

img = cv2.imread(img_path)
img = cv2.resize(img, (150, 150))
img = np.expand_dims(img, axis=0)  # Tambahkan batch dimension
img = img / 255.0  # Normalisasi

# Prediksi
pred = modelan.predict(img)
print("Prediksi kelas:", np.argmax(pred))

from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
modelan = load_model("classification_modelTFL.h5")

# Baca gambar baru
# img_path = "path/to/new/image.jpg"
img_path = "seg_test/seg_test/street/20066.jpg" #street

img = cv2.imread(img_path)
img = cv2.resize(img, (150, 150))
img = np.expand_dims(img, axis=0)  # Tambahkan batch dimension
img = img / 255.0  # Normalisasi

# Prediksi
pred = modelan.predict(img)
print("Prediksi kelas:", np.argmax(pred))

"""### model.TFlite"""

interpreter = tf.lite.Interpreter(model_path='tf_lite/model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load labels
with open('tf_lite/labels.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (150, 150))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

image_path = "seg_test/seg_test/buildings/20057.jpg" #buildings
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

image_path = "seg_test/seg_test/forest/20056.jpg" #forest
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

image_path = "seg_test/seg_test/glacier/20059.jpg" #glacier
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

image_path = "seg_test/seg_test/mountain/20058.jpg" #mountain
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

image_path = "seg_test/seg_test/sea/20072.jpg" #sea
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

image_path = "seg_test/seg_test/street/20066.jpg" #street
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

"""data di folder pred"""

image_path = "seg_pred/seg_pred/10013.jpg" #mountain
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

image_path = "seg_pred/seg_pred/10021.jpg" #forest
input_data = preprocess_image(image_path)

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

predicted_class_idx = np.argmax(output_data, axis=1)[0]
predicted_class = labels[predicted_class_idx]
print('Predicted Class:', predicted_class)

"""## Requirements"""

# Dengan pipreqs
# 1. Install pipreqs cukup 1x
# !pip install pipreqs

#2. Hubungkan Google Drive
from google.colab import drive
drive.mount('/content/drive')

# # 4. Gunakan pipreqs untuk membuat file requirements.txt
!pipreqs "/content/drive/My Drive/Latihan Python/project"
!pipreqs "/content/drive/My Drive/Latihan Python/project" --print
!pipreqs "/content/drive/My Drive/Latihan Python/project" --force

# # 5. Unduh file requirements.txt
# from google.colab import files
# files.download('/content/drive/My Drive/Latihan Python/project/requirements.txt')
# # files.download('requirements.txt')

# dengan pip freeze
# !pip freeze > requirements.txt
# from google.colab import files
# # # files.download('/content/drive/My Drive/Latihan Python/project/requirements.txt')
# langsung download
# files.download('requirements.txt')