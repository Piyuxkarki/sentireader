import config as _

from loguru import logger

from ml.model import Model


def main():
    while True:
        Model.predict(Model.load_model('models/model.pkl'), [input('Enter a sentence: ')])


if __name__ == '__main__':
    main()