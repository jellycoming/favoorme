# coding=utf-8
"""
:: root logger是所有logger对象的父类, 子类logger中如没有level、 handler等设置, 日志信息将传递给root logger处理(子类logger.propagate不能为False)
:: 设置logger对象的日志级别是必须的, 而handler对象的日志级别设置是可选的
"""
import logging

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

logger = logging.getLogger()
# 日志信息不向上传递
logger.propagate = False


def _set_level(level):
    logger.setLevel(level=level)


def set_stream_handler(level=DEBUG):
    _set_level(level=level)  # 必须得
    sh = logging.StreamHandler()
    sh.setLevel(level=level)  # 可选的
    sh.setFormatter(fmt=_get_formatter())
    logger.addHandler(sh)


def set_file_handler(filename, level=DEBUG):
    _set_level(level=level)
    fh = logging.FileHandler(filename=filename)
    fh.setLevel(level=level)
    fh.setFormatter(fmt=_get_formatter())
    logger.addHandler(fh)


def disable_logger(logger_name):
    nh = logging.NullHandler()
    nh.setLevel(logging.DEBUG)
    logging.getLogger(logger_name).addHandler(nh)
    logging.getLogger(logger_name).propagate = False


def _get_formatter():
    fmt = '%(asctime)-15s %(name)s %(message)s (%(filename)s %(lineno)d) [%(levelname)s]'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    return formatter