"""
Imports

"""
import struct
from hashlib import sha256

"""
General variables

This has variables that are important to the comunication

"""

PORT = 52377

"""
Enums

this has type enum and subtypes enums
the value of the enum is the value of the type in the protocol

"""


class Type:
    # general
    ERROR = 0

    # control/initial
    NAME = 1
    ID = 2
    BOARD = 3
    DISCONNECTION = 4
    INITIAL = 5

    # management/update
    SNAKE = 6
    ORB = 7


class Subtype:
    class ERROR:
        name_error = 0
        full_server = 1

    class NAME:
        request = 0
        response = 1

    class ID:
        send = 0
        confirm = 1

    class BOARD:
        send_dimensions = 0
        confirm_dimensions = 1
        request_location = 2
        send_location = 3

    class DISCONNECTION:
        announce = 0
        confirm = 1

    class SNAKE:
        new = 0
        full_update = 1
        delete = 2
        change_angle = 3

    class ORB:
        new = 0
        delete = 1

    class INITIAL:
        server = 0
        client = 1


"""
Builders

this has functions to build all the possible message types

"""


def error_name_error():
    message = 'This name is already taken.'
    return struct.pack('!HH', Type.ERROR, Subtype.ERROR.name_error) + message


def error_full_server():
    message = 'Server in full entry denied'
    return struct.pack('!HH', Type.ERROR, Subtype.ERROR.full_server) + message


def name_request():
    return struct.pack('!HH', Type.NAME, Subtype.NAME.request)


def name_response(name):
    data = struct.pack('!HH', Type.NAME, Subtype.NAME.response)
    data += name
    return data


def id_send(id_):
    return struct.pack('!HH', Type.ID, Subtype.ID.send) + id_


def id_confirm():
    return struct.pack('!HH', Type.ID, Subtype.ID.confirm)


def board_send_dimensions(width, height):
    return struct.pack('!HHHH', Type.BOARD, Subtype.BOARD.send_dimensions, width, height)


def board_confirm_dimensions():
    return struct.pack('!HHHH', Type.BOARD, Subtype.BOARD.confirm_dimensions)


def board_request_location():
    return struct.pack('!HH', Type.BOARD, Subtype.BOARD.request_location)


def board_send_location(x, y):
    return struct.pack('!HHff', Type.BOARD, Subtype.BOARD.send_location, x, y)


def disconnection_announce():
    return struct.pack('!HH', Type.DISCONNECTION, Subtype.DISCONNECTION.announce)


def disconnection_confirm():
    return struct.pack('!HH', Type.DISCONNECTION, Subtype.DISCONNECTION.confirm)


def snake_new(id_, name, mass, head, tail):
    data = struct.pack('!HH', Type.SNAKE, Subtype.SNAKE.new)
    data += id_
    data += struct.pack('!b', len(name))
    data += name
    data += struct.pack('!l', mass)
    x, y = head
    data += struct.pack('!ff', x, y)
    for x, y in tail:
        data += struct.pack('!ff', x, y)
    return data


def snake_full_update(id_, mass, head, tail):
    data = struct.pack('!HH', Type.SNAKE, Subtype.SNAKE.full_update)
    data += id_
    data += struct.pack('!l', mass)
    x, y = head
    data += struct.pack('!ff', x, y)
    for x, y in tail:
        data += struct.pack('!ff', x, y)
    return data


def snake_delete(id_):
    data = struct.pack('!HH', Type.SNAKE, Subtype.SNAKE.delete)
    data += id_
    return data


def snake_change_angle(angle):
    data = struct.pack('!HHf', Type.SNAKE, Subtype.SNAKE.change_angle, angle)
    return data


def orb_new(id_, value, x, y):
    data = struct.pack('!HH', Type.ORB, Subtype.ORB.new)
    data += id_
    data += struct.pack('!bff', value, x, y)
    return data


def orb_delete(id_):
    data = struct.pack('!HHff', Type.ORB, Subtype.ORB.delete)
    data += id_
    return data


def initial_server(width, height, id_):
    data = struct.pack('!HHHH', Type.INITIAL, Subtype.INITIAL.server, width, height)
    data += id_
    return data


def initial_client(name):
    data = struct.pack('!HH', Type.INITIAL, Subtype.INITIAL.client)
    data += name
    return data


"""
Protocol Parsing

this section has all the code that parsers given recived data.
this has three parts.
- individuals parsers for each protocol message types.  
- dispatcher that connects types to their function.
- general parsing function.

"""


def __error_parser(data):
    kwargs = {}
    kwargs['message'] = data
    return kwargs


def __name_request_parser(data):
    kwargs = {}
    return kwargs


def __name_response_parser(data):
    kwargs = {}
    kwargs['name'] = data
    return kwargs


def __id_send_parser(data):
    kwargs = {}
    kwargs['id'] = data
    return kwargs


def __id_confirm_parser(data):
    kwargs = {}
    return kwargs


def __board_send_dimensions_parser(data):
    kwargs = {}
    kwargs['width'] = struct.unpack('!H', data[:2])[0]
    kwargs['height'] = struct.unpack('!H', data[2:])[0]
    return kwargs


def __board_confirm_dimensions_parser(data):
    kwargs = {}
    return kwargs


def __board_request_location_parser(data):
    kwargs = {}
    return kwargs


def __board_send_location_parser(data):
    kwargs = {}
    kwargs['x'] = struct.unpack('!f', data[:4])[0]
    kwargs['y'] = struct.unpack('!f', data[4:])[0]
    return kwargs


def __disconnection_announce_parser(data):
    kwargs = {}
    return kwargs


def __disconnection_confirm_parser(data):
    kwargs = {}
    return kwargs


def __snake_new_parser(data):
    kwargs = {}
    kwargs['id'] = data[:KEY_SIZE]
    data = data[KEY_SIZE:]
    name_len = struct.unpack('!b', data[0:1])
    data = data[1:]
    kwargs['name'] = data[:name_len]
    data = data[:name_len]
    kwargs['mass'] = struct.unpack('!l', data[:4])
    data = data[4:]
    x, y = struct.unpack('!ff', data[:8])
    kwargs['head'] = (x, y)
    data = data[:8]
    tail = []
    while data:
        x, y = struct.unpack('!ff', data[:8])
        tail.append((x, y))
        data = data[:8]
    kwargs['tail'] = tail
    return kwargs


def __snake_full_update_parser(data):
    kwargs = {}
    kwargs['id'] = data[:KEY_SIZE]
    data = data[KEY_SIZE:]
    kwargs['mass'] = struct.unpack('!l', data[:4])
    data = data[4:]
    x, y = struct.unpack('!ff', data[:8])
    kwargs['head'] = (x, y)
    data = data[:8]
    tail = []
    while data:
        x, y = struct.unpack('!ff', data[:8])
        tail.append((x, y))
        data = data[:8]
    kwargs['tail'] = tail
    return kwargs


def __snake_delete_parser(data):
    kwargs = {}
    kwargs['id'] = data
    return kwargs


def __snake_change_angle_parser(data):
    kwargs = {}
    kwargs['angle'] = float(struct.unpack('!f', data)[0])
    return kwargs


def __orb_new_parser(data):
    kwargs = {}
    kwargs['id'] = data[:32]
    kwargs['value'] = struct.unpack('!b', data[32:33])[0]
    kwargs['x'] = struct.unpack('!f', data[33:37])[0]
    kwargs['y'] = struct.unpack('!f', data[37:41])[0]
    return kwargs


def __orb_delete_parser(data):
    kwargs = {}
    kwargs['id'] = data
    return kwargs


def __initial_server_parser(data):
    kwargs = {}
    kwargs['width'] = struct.unpack('!H', data[:2])[0]
    kwargs['height'] = struct.unpack('!H', data[2:4])[0]
    kwargs['id'] = data[4:]
    return kwargs


def __initial_client_parser(data):
    kwargs = {}
    kwargs['name'] = data
    return kwargs


DISPATCHER = {
    (Type.ERROR, Subtype.ERROR.name_error): __error_parser,
    (Type.ERROR, Subtype.ERROR.full_server): __error_parser,
    (Type.NAME, Subtype.NAME.request): __name_request_parser,
    (Type.NAME, Subtype.NAME.response): __name_response_parser,
    (Type.ID, Subtype.ID.send): __id_send_parser,
    (Type.ID, Subtype.ID.confirm): __id_confirm_parser,
    (Type.BOARD, Subtype.BOARD.send_dimensions): __board_send_dimensions_parser,
    (Type.BOARD, Subtype.BOARD.confirm_dimensions): __board_confirm_dimensions_parser,
    (Type.BOARD, Subtype.BOARD.request_location): __board_request_location_parser,
    (Type.BOARD, Subtype.BOARD.send_location): __board_send_location_parser,
    (Type.DISCONNECTION, Subtype.DISCONNECTION.announce): __disconnection_announce_parser,
    (Type.DISCONNECTION, Subtype.DISCONNECTION.confirm): __disconnection_confirm_parser,
    (Type.SNAKE, Subtype.SNAKE.new): __snake_new_parser,
    (Type.SNAKE, Subtype.SNAKE.full_update): __snake_full_update_parser,
    (Type.SNAKE, Subtype.SNAKE.delete): __snake_delete_parser,
    (Type.SNAKE, Subtype.SNAKE.change_angle): __snake_change_angle_parser,
    (Type.ORB, Subtype.ORB.new): __orb_new_parser,
    (Type.ORB, Subtype.ORB.delete): __orb_delete_parser,
    (Type.INITIAL, Subtype.INITIAL.server):__initial_server_parser,
    (Type.INITIAL, Subtype.INITIAL.client):__initial_client_parser,
}


def parse(data):
    kwargs = {}
    kwargs['type'] = struct.unpack('!H', data[0:2])[0]
    kwargs['subtype'] = struct.unpack('!H', data[2:4])[0]

    special_kwargs = DISPATCHER[kwargs['type'], kwargs['subtype']](data[4:])
    kwargs.update(special_kwargs)

    return kwargs


"""
Additional functions

"""


def add_length(data):
    length = len(data)

    if length > 65536:
        raise ValueError(
            'length of the packet cant be mor than 65536. ({})'.format(length))

    length = struct.pack('!H', len(data))
    return length + data


KEY_SIZE = 256


def key(obj):
    return sha256(str(id(obj))).digest()


"""
IO Functions

this functions use a length before the message for safe transfer

"""


def send_data(sock, data):
    sock.send(add_length(data))
    print 'send >', repr(add_length(data))


LENGTH_HEADER_SIZE = 2


def recv_data(sock):
    length_str = ''
    length = 0
    sock.settimeout(None)
    while len(length_str) < LENGTH_HEADER_SIZE:
        length_str += sock.recv(LENGTH_HEADER_SIZE - len(length_str))
        if length_str == '':
            break

    data = ''
    if length_str != '':
        length = struct.unpack('!H', length_str)[0]

        while len(data) < length:
            data += sock.recv(length - len(data))
            if data == '':
                break

    if length != len(data):
        data = ''

    print 'recv >', repr(data)
    return data
