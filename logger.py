
import logging
import logging.handlers
import os
import os.path
import sys
from systemd.journal import JournalHandler


# {}-formatting adapter taken from logging cookbook:
#   https://docs.python.org/3/howto/logging-cookbook.html#use-of-alternative-formatting-styles

class Message():
    def __init__(self, fmt, args):
        self.fmt = fmt
        self.args = args

    def __str__(self):
        return self.fmt.format(*self.args)


class StyleAdapter(logging.LoggerAdapter):
    """
    A wrapper around a ``logging.Logger`` object that adds ``str.format()`` capabilities so you can
    do things like::

        logger.debug('found {} records', len(my_records))

    without calling ``format()`` directly and without incurring the cost of calling it if the
    current log level would prevent this statement from actually being logged.

    When you ``from logger import logger``, this is the object you get.
    """

    def __init__(self, logger, extra = None):
        super().__init__(logger, extra or {})
        self._duplicated_to_stderr = False


    def log(self, level, msg, *args, **kwargs):
        """
        Implements the ``str.format()`` logic. You probably shouldn't be calling this method
        directly.
        """
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, Message(msg, args), (), **kwargs)


    def setFormat(self, fmt, style = '{'):
        """
        A convenience wrapper so you don't have to instantiate a ``logging.Formatter`` object to
        override the log statement format.

        See the standard library docs for more details. Generally, you won't need to call this
        method.
        """
        formatter = logging.Formatter(fmt, style = style)
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)


    def getLevel(self):
        """
        A convenience wrapper around ``getEffectiveLevel()`` because the integer values for the
        various logging levels are clunky and probably don't mean anything to you.

        Returns:
            str: the name of the effective log level for this logging object, in lowercase
            (``"warning"``, ``"info"``, etc.)
        """
        level = self.getEffectiveLevel()
        if level == logging.CRITICAL:
            return 'critical'
        elif level == logging.ERROR:
            return 'error'
        elif level == logging.WARNING:
            return 'warning'
        elif level == logging.INFO:
            return 'info'
        elif level == logging.DEBUG:
            return 'debug'
        elif level == logging.NOTSET:
            return 'notset'
        else:
            return 'unknown ({})'.format(level)


    def setLevel(self, lvl):
        """
        A convenience wrapper around the super method of the same name, because upper case sucks.

        Args:
            lvl (str): a standard logging level name (``"warning"``, ``"debug"``, etc.); will be
                cast to upper case for you, since the super method is strict about that

        Notes:

            * the super method also accepts integer values from the logging.LEVEL_NAME constants,
              those will be passed through, even though the above docs state that ``lvl`` should
              be a ``str``.
        """
        if isinstance(lvl, str):
            return super().setLevel(lvl.upper())
        else:
            return super().setLevel(lvl)


    def duplicateToStderr(self):
        """
        Add a handler to the logger that also sends messages to ``stderr`` in addition to the
        journal. After called the first time, subsequent calls to this method will do nothing.
        """
        if not self._duplicated_to_stderr:
            self.logger.addHandler( logging.StreamHandler())
            self._duplicated_to_stderr = True


_logger = logging.getLogger(__name__)
_handler = JournalHandler(SYSLOG_IDENTIFIER = os.path.basename( sys.argv[0]))
_logger.addHandler(_handler)

logger = StyleAdapter(_logger)

_log_level = os.getenv( 'SUDO_LOGGER' )

if _log_level is None:
    # no ENV var set
    logger.setLevel( logging.INFO )
elif _log_level.lower() in { 'critical', 'error', 'warning', 'info', 'debug' }:
    logger.setLevel( _log_level )
else:
    logger.setLevel( logging.INFO )
    logger.warning( 'unrecognized SUDO_LOGGER value {!r}, defaulting to INFO', _log_level )

