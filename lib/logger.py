# coding=utf-8
import logging

logger = logging.getLogger(name='application')
logger.propagate = False  # 日志信息不向上传递


def _get_formatter():
    fmt = '%(asctime)-15s - %(levelname)s - %(name)s - %(filename)s %(lineno)d - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    return formatter


def set_logger_file_handler(filename, level=logging.DEBUG):
    fh = logging.FileHandler(filename=filename)
    fh.setLevel(level=level)
    fh.setFormatter(fmt=_get_formatter())
    logger.addHandler(fh)


def set_logger_stream_handler(level=logging.DEBUG):
    sh = logging.StreamHandler()
    sh.setLevel(level=level)
    sh.setFormatter(fmt=_get_formatter())
    logger.addHandler(sh)

# sub logger 会继承父类logger application的相关配置,可在其他模块直接import后使用
sub_logger = logging.getLogger('application.subname')