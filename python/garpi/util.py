import logging, logging.handlers, sys,os

def stderr(s):
    sys.stderr.write(str(s)+'\n')
    return s
def try_traceback(a):
    try:
        a.printTraceback(sys.stderr)
    except:
        pass

from logging import _srcfile
class Logger(logging.Logger):
    def debug(self, msg, *args, **kwargs):
        logging.Logger.debug(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def info(self, msg, *args, **kwargs):
        logging.Logger.info(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def warning(self, msg, *args, **kwargs):
        logging.Logger.warning(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def error(self, msg, *args, **kwargs):
        logging.Logger.error(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def critical(self, msg, *args, **kwargs):
        logging.Logger.critical(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg

    def findCaller(self):
        f = sys._getframe(2)
        while 1:
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back.f_back
                continue
            return filename, f.f_lineno, ""


logname = "garpi.log"
log = Logger(logname)
def setup(logfile):
    rfh = logging.handlers.RotatingFileHandler(logfile,'a',10e6,50)
    rfh.setLevel(logging.DEBUG)
    log.setLevel(logging.INFO)
    f = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(module)s:%(lineno)d - %(message)s')
    rfh.setFormatter(f)
    log.addHandler(rfh)
    return log
