import tensorflow
import ktrain
from ktrain import text
import pandas as pd
from sklearn.model_selection import train_test_split
import seaborn as sns
import os


seed = 4242
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

csv_file = 'bert_training_data.csv'
data = pd.read_csv(csv_file)
print(data.head(5))

epochs = 5
learning_rate = 2e-5
batch_size = 128
max_length = 17
max_words = 10000

sequences = data['title'].values
labels = data[['positive_change_+1day', 'negative_change_+1day']].values

x_train, x_test, y_train, y_test = train_test_split(sequences, labels, random_state=seed, test_size=0.2)

MODEL = 'distilbert-base-uncased'
class_names = ['negative', 'positive']

transformer = text.Transformer(MODEL, maxlen=max_length, class_names=class_names)
train_data = transformer.preprocess_train(x_train, y_train)
val_data = transformer.preprocess_test(x_test, y_test)

model = transformer.get_classifier()
learner = ktrain.get_learner(model, train_data=train_data, val_data=val_data, batch_size=batch_size)

learner.fit_onecycle(learning_rate, epochs)

confusion = learner.evaluate()

cm_df = pd.DataFrame(confusion, class_names, class_names)
sns.set(font_scale=1.1, font='Arial')
ax = sns.heatmap(cm_df, cmap='Blues', annot=True, annot_kws={'size': 11}, cbar=False, fmt='g')
ax.set_xlabel('Actual')
ax.set_ylabel('Predicted')

