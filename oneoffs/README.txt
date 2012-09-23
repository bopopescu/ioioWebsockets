pyIOIOWebsockets oneoffs

This is a collection of libraries and applications designed to provide access to an IOIO device via websocket connections - allowing not only access via standalone applications, but also from within a web browser itself[which is normally sandboxed and not allowed to access hardware devices such as serial ports, usb devices, or bluetooth connections]

Packages:
**echoWebsocket**
Doesn't do anything with IOIO, simply runs a websocket server on port 9000 that will echo a message back to the client
echoWebsocket.py -- python websocket server using twisted and autobahn, port set in sourcecode
echoWebsocketClient.html -- html/javascript page to connect to websocket server and send a message

**ioioConsole**
ioioConsole.py -- ugly miniterm hack to verify that python can communicate with the ioio.  Since it treats input as text, not much you can do with it.  Ctr+T for the menu, followed by a lowercase l to turn on the led, and a lowerface f to turn it off

**ioioWebsocket**
IOIOwebsocket.py  -- ugly miniterm and echoWebsocket hack to link a websocket client to the ioio.  Hardcoded to use com port 4 for the ioio and port 9001 for the socket
ioioWebsocketClient.html -- 2 simple buttons, after connecting press led on to turn on the led, led off to turn it off

Python applicationa use a number of add on modules:
  pyserial: http://pyserial.sourceforge.net/
  twisted
  autobahn python: http://autobahn.ws/python

Of specific note for developers is the pyserial module.  When installed, it will install a large number of sample programs which can be used with extremely little modification with the IOIO:
pyBusPirateLite and pyBusPirateLite1:  controls a buspirate microprocessor programmer via a serial connection.  This includes programatic access to i2c and spi - 2 protocols that the IOIO also allows access to.  Change the commands to match and you can write python applications to use i2c.
oscope_v1.2.py:

Also refer to rfc
Attatches to some sort of microcontoller via the serial connection and starts reading the adc and charts the values.  Just needs a small ammount of changes in commands to accomodate the IOIO protocol.

