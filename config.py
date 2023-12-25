import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, format='> <level>{message}</level>')
logger.add('logs/game.log', mode='w', format='[{elapsed}] [{name}: {line}] > {message}')