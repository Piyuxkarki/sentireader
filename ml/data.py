import pprint
from collections import Counter

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import neattext.functions as nfx
from loguru import logger


class Data(object):

    @staticmethod
    def analyze_data(path: str) -> None:
        """
        Gives an analysis of the data
        """

        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            return
        
        print(f'{data.head()}')
        print(f'Row count: {len(data)}')
        print(f'Column Count: {len(data.columns)}')
        print(f'Columns: {data.columns.tolist()}')

    @staticmethod
    def analyze_data_column(path: str, column: str) -> None:
        """
        Gives an analysis of a particular column of the data
        """

        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            return
        
        try: column_data: pd.Series = data[column]
        except KeyError: 
            logger.error(f'Column {column} does not exist')
            return
        print(f'Column analysis ({column}):')
        pprint.pprint(column_data.value_counts().to_dict())

        # Plot
        plt.figure(figsize=(8, 6))
        sns.countplot(data, x=column, palette='viridis')
        plt.title(f'Value counts of {column} column')
        plt.xlabel(column)
        plt.ylabel('Count')
        plt.show()

    @staticmethod
    def get_unique_values(path: str, column: str):
        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            return
        
        try: column_data: pd.Series = data[column]
        except KeyError: 
            logger.error(f'Column {column} does not exist')
            return
        
        return column_data.unique().tolist()

    @staticmethod
    def preprocess(path: str, output: str, emotion_column: str, emotions_to_keep: list[str]) -> None:
        """
        - Converts all input text into lowercase.
        - Filters out only the most common emotions which are:
            - Happy
            - Sad
            - Angry
            - Neutral
        """
        
        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            return

        try: data[emotion_column]
        except KeyError: 
            logger.error(f'Column {emotion_column} does not exist')
            return
        
        data = data[data[emotion_column].isin(emotions_to_keep)]
        data.to_csv(output, index=False)

    @staticmethod
    def clean(path: str, output: str, sentence_column: str) -> None:
        """
        - Remove emojies
        - Remove userhandles
        - Remove hashtags
        - Remove accents
        - Remove contractions
        - Remove punctuations
        - Remove bad quotes
        - Remove stopwords
        """

        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            return
        
        try: data[sentence_column]
        except KeyError: 
            logger.error(f'Column {sentence_column} does not exist')
            return
        
        data['Clean'] = data[sentence_column].apply(nfx.remove_emojis)
        data['Clean'] = data['Clean'].apply(nfx.remove_punctuations)
        data['Clean'] = data['Clean'].apply(nfx.remove_bad_quotes)
        data['Clean'] = data['Clean'].apply(nfx.fix_contractions)
        data['Clean'] = data['Clean'].apply(nfx.remove_userhandles)
        data['Clean'] = data['Clean'].apply(nfx.remove_hashtags)
        data['Clean'] = data['Clean'].apply(nfx.remove_accents)
        data['Clean'] = data['Clean'].apply(nfx.remove_stopwords)
        data['Clean'] = data['Clean'].apply(lambda text: '.' if text == '' else text)

        data.to_csv(output, index=False)

    @staticmethod
    def extract_keywords(text: str, emotion_name: str, num: int = 100, plot: bool = False) -> dict[str, int]:
        tokens = text.split()
        most_common = dict(Counter(tokens).most_common(num))

        if plot:
            df: pd.DataFrame = pd.DataFrame(most_common.items(),  columns=['token', 'count'])
            plt.figure(figsize=(20, 10))
            plt.title(f'Plot of {emotion_name}')
            sns.barplot(x='token', y='count', data=df)
            plt.xticks(rotation=60)
            plt.show()
        
        return dict(most_common)
    
    @staticmethod
    def extract_emotion_keyword(path: str, emotion_column: str, text_column: str, plot: bool = False, num: int = 100) -> dict[str, dict[str, int]]:
        """
        Returns the most common keywords for each emotion
        """

        try: data: pd.DataFrame = pd.read_csv(path)
        except FileNotFoundError:
            logger.error(f'{path} not found')
            return {}
        
        try: 
            data[emotion_column]
            data[text_column]
        except KeyError: 
            logger.error('Column does not exist')
            return {}
        
        emotion_list = data[emotion_column].unique().tolist()

        keywords: dict[str, dict[str, int]] = {}

        for emotion in emotion_list:
            emotion_data = data[data[emotion_column] == emotion][text_column].tolist()
            emotion_data = list(map(str, emotion_data))
            emotion_data = ' '.join(emotion_data)
            keywords[emotion] = Data.extract_keywords(emotion_data, emotion, num, plot)
            
        return keywords
