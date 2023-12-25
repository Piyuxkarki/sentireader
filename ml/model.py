import sys

import pandas as pd
import joblib
import torch
import torch.nn as nn
import transformers
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from loguru import logger
    

class Model(object):

    @staticmethod
    def create_model() -> Pipeline:
        return Pipeline([
            ('vect', CountVectorizer()),    # Count Vectorization
            ('tfidf', TfidfTransformer()),  # TF-IDF Transformation
            ('clf', MultinomialNB())        # Multinomial Naive Bayes Classifier
        ])
    
    @staticmethod
    def save_model(model: Pipeline, path: str) -> None:
        joblib.dump(model, path)

    @staticmethod
    def load_model(path: str) -> Pipeline:
        return joblib.load(path)
    
    @staticmethod
    def get_train_test_split(path: str, text_column: str, emotion_column: str):

        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            sys.exit()
        
        try: 
            X = data[text_column]
            y = data[emotion_column]
        except KeyError: 
            logger.error('Column does not exist')
            sys.exit()

        return train_test_split(X, y, test_size=0.2)
    
    @staticmethod
    def train_model(model: Pipeline, x_train, y_train) -> None:
        model.fit(x_train, y_train)

    @staticmethod
    def predict(model: Pipeline, input_data: list[str]) -> None:
        classes_ = list(model.classes_)
        predictions_prob = list(model.predict_proba(input_data)[0])

        probability_dict = dict(zip(classes_, predictions_prob))

        max_probability = max(probability_dict.values())
        max_emotion = [emotion for emotion, prob in probability_dict.items() if prob == max_probability][0]

        # logger.debug(f"'{max_emotion}' with the probability of {max_probability*100:.4f}%.")

        return max_emotion
    


class SentiReader(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.bert = transformers.BertModel.from_pretrained('bert-base-cased')
        self.drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, input_ids, attention_mask):
        pooler_output = self.bert(input_ids=input_ids,
                                  attention_mask=attention_mask)['pooler_output']
        output = self.drop(pooler_output)
        output = self.out(output)
        return self.softmax(output)


class NewModel(object):

    @staticmethod
    def load_model(path: str) -> SentiReader:
        model = SentiReader(3)
        model.load_state_dict(torch.load(path))
        return model