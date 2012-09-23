__author__ = 'gmort'
#!c:\Python27\python.exe

# Very simple IOIO control terminal with built in led on/off

import sys, os, serial, threading
from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory,\
    WebSocketServerProtocol,\
    listenWS

# Configure the serial port

NO_SYNC = 0
RISING_SLOPE = 1
FALLING_SLOPE = 2

#change this path
SCOPE_PORT="com4"
SCOPE_BAUD=57600

#TTY Configs
CONVERT_CRLF = 2
CONVERT_CR   = 1
CONVERT_LF   = 0
NEWLINE_CONVERISON_MAP = ('\n', '\r', '\r\n')
LF_MODES = ('LF', 'CR', 'CR/LF')

REPR_MODES = ('raw', 'some control', 'all control', 'hex')

RES_X = 640
RES_Y = 480
MAX_VOLTAGE = 6
OFFSET = 10
TRIGGER_LEV_RES = 0.05
TRIG_CAL = 0.99
DEFAULT_TIME_DIV = 1
DEFAULT_TRIGGER_LEV = 1.0
DEFAULT_TRIGGER_MODE = 0



DATA_RATE = 5720.0 #measures/second (estimated experimenticaly)

DEFAULT_TIME_SCALE = RES_X / DATA_RATE #default time in seconds to make one window fill

if sys.version_info >= (3, 0):
    def character(b):
        return b.decode('latin1')
else:
    def character(b):
        return b


class Miniterm(object):
    def __init__(self, port, baudrate, parity, rtscts, xonxoff, echo=False, convert_outgoing=CONVERT_CRLF, repr_mode=0):
        try:
            self.serial = serial.serial_for_url(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        except AttributeError:
            # happens when the installed pyserial is older than 2.5. use the
            # Serial class directly then.
            self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        self.echo = echo
        self.repr_mode = repr_mode
        self.convert_outgoing = convert_outgoing
        self.newline = NEWLINE_CONVERISON_MAP[self.convert_outgoing]
        self.dtr_state = True
        self.rts_state = True
        self.break_state = False

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        self.receiver_thread.join()


    def start(self):
        self.alive = True
        self._start_reader()
        # enter console->serial loop
        #self.transmitter_thread = threading.Thread(target=self.writer)
        #self.transmitter_thread.setDaemon(True)
        #self.transmitter_thread.start()

    def stop(self):
        self.alive = False

    def join(self, transmit_only=False):
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()

    def dump_port_settings(self):
        sys.stderr.write("\n--- Settings: %s  %s,%s,%s,%s\n" % (
            self.serial.portstr,
            self.serial.baudrate,
            self.serial.bytesize,
            self.serial.parity,
            self.serial.stopbits))
        sys.stderr.write('--- RTS: %-8s  DTR: %-8s  BREAK: %-8s\n' % (
            (self.rts_state and 'active' or 'inactive'),
            (self.dtr_state and 'active' or 'inactive'),
            (self.break_state and 'active' or 'inactive')))
        try:
            sys.stderr.write('--- CTS: %-8s  DSR: %-8s  RI: %-8s  CD: %-8s\n' % (
                (self.serial.getCTS() and 'active' or 'inactive'),
                (self.serial.getDSR() and 'active' or 'inactive'),
                (self.serial.getRI() and 'active' or 'inactive'),
                (self.serial.getCD() and 'active' or 'inactive')))
        except serial.SerialException:
            # on RFC 2217 ports it can happen to no modem state notification was
            # yet received. ignore this error.
            pass
        sys.stderr.write('--- software flow control: %s\n' % (self.serial.xonxoff and 'active' or 'inactive'))
        sys.stderr.write('--- hardware flow control: %s\n' % (self.serial.rtscts and 'active' or 'inactive'))
        sys.stderr.write('--- data escaping: %s  linefeed: %s\n' % (
            REPR_MODES[self.repr_mode],
            LF_MODES[self.convert_outgoing]))

    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and self._reader_alive:
                data = character(self.serial.read(1))

                if self.repr_mode == 0:
                    # direct output, just have to care about newline setting
                    if data == '\r' and self.convert_outgoing == CONVERT_CR:
                        sys.stdout.write('\n')
                    else:
                        sys.stdout.write(data)
                elif self.repr_mode == 1:
                    # escape non-printable, let pass newlines
                    if self.convert_outgoing == CONVERT_CRLF and data in '\r\n':
                        if data == '\n':
                            sys.stdout.write('\n')
                        elif data == '\r':
                            pass
                    elif data == '\n' and self.convert_outgoing == CONVERT_LF:
                        sys.stdout.write('\n')
                    elif data == '\r' and self.convert_outgoing == CONVERT_CR:
                        sys.stdout.write('\n')
                    else:
                        sys.stdout.write(repr(data)[1:-1])
                elif self.repr_mode == 2:
                    # escape all non-printable, including newline
                    sys.stdout.write(repr(data)[1:-1])
                elif self.repr_mode == 3:
                    # escape everything (hexdump)
                    for c in data:
                        sys.stdout.write("%s " % c.encode('hex'))
                sys.stdout.flush()
        except serial.SerialException, e:
            self.alive = False
            # would be nice if the console reader could be interruptted at this
            # point...
            raise


class EchoServerProtocol(WebSocketServerProtocol):

    try:
      ioioboard =  Miniterm(
        SCOPE_PORT,
        SCOPE_BAUD,
        'N',
        False,
        False,
        True,
        CONVERT_CRLF,
        'raw',
        )
    except serial.SerialException, e:
        sys.stdout.write("could not open port %r: %s\n" % (SCOPE_PORT, e))
        sys.stdout.flush()
        sys.exit(1)


    def onMessage(self, msg, binary):
        self.ioioboard.serial.write(msg)
        self.sendMessage("Finshed sending command {0:>s} with parm {1:>s}\n".format(ord(msg[0]), ord(msg[1])))
        #self.sendMessage(ord(msg[0]))
        #self.sendMessage(ord(msg[1]))

if __name__ == '__main__':
    factory = WebSocketServerFactory("ws://localhost:9001")
    factory.protocol = EchoServerProtocol
    listenWS(factory)
    reactor.run()


