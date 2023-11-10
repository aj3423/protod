import sys
import re
import argparse
import protod 
from termcolor import cprint

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, help='file path that contains proto data')
parser.add_argument('--hex', action='store_true', help='content is hex string, eg: "080102..."')
parser.add_argument('--b64', action='store_true', help='content is base64')
parser.add_argument('--max_bin', metavar='n', type=int, default=32, help='binary exceeds `n` bytes is truncated and followed by a "..."')
parser.add_argument('rest', help='hex string to parse, eg: "08 01..."', nargs=argparse.REMAINDER)

args = parser.parse_args()

proto = bytes()

# clear all ' \t\n\r' of an str
def cleanup(s:str) -> str:
    return re.sub(r'[\n\r\t ]+', '', s)

if args.file is not None: # get proto from file
    try:
        f = open(args.file, "rb")
        proto = f.read()
        f.close()
    except:
        cprint(f'failed to read file: {args.file}', 'red')
        sys.exit(1)

    if args.b64 or args.hex:
        proto = cleanup(proto)
else: # get proto from arguments
    if len(args.rest) == 0:
        cprint(f'no input', 'red')
        parser.print_help()
        sys.exit(1)

    if len(args.rest) > 1: # multiple rest arguments, eg: pro 0a 08 01 ...
        # concat them together
        proto = cleanup(''.join(args.rest))
    else:
        # single rest argument, eg: pro "0a 08 01 ..."
        proto = cleanup(args.rest[0])

# the proto should've already been cleaned up
if args.b64:
    try:
        import base64
        proto = base64.b64decode(proto)
    except:
        cprint(f'invalid b64 data', 'red')
        sys.exit(1)

if type(proto) == str and re.match(r'^([0-9A-Fa-f]+)$', proto):
    args.hex = True

if args.hex:
    proto = bytes.fromhex(proto)

s = protod.dump(
    proto, 
    protod.ConsoleRenderer(
        truncate_after=args.max_bin
   )
)
print(s)

# Just a workaround for `pip install`
# the `protod = 'protod.main:dummy'` in pyproject.toml needs to call a function 
def dummy():
    pass

