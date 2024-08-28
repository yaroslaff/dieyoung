import argparse
import psutil
import os
import rich
import re
import time

__version__ = '0.0.1'

args = None
max_age = 0

def seconds2human(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts = []
    if h > 0:
        parts.append(f"{h}h")
    if m > 0:
        parts.append(f"{m}m")
    if s > 0 or not parts:  # Include seconds even if 0 if no other parts exist
        parts.append(f"{s}s")
    return "".join(parts)

import re

def human2seconds(human_readable: str):
    time_units = {'h': 3600, 'm': 60, 's': 1}
    pattern = re.compile(r'(\d+)\s*([hms]?)')
    matches = pattern.findall(human_readable)
    total_seconds = 0
    for value, unit in matches:
        if unit == '':  # No suffix means seconds
            unit = 's'
        total_seconds += int(value) * time_units[unit]
    return total_seconds



def get_args():

    def_time = '0s'

    parser = argparse.ArgumentParser(    
        description='Find/kill processes by name and arguments',
        formatter_class=argparse.RawTextHelpFormatter)
    g = parser.add_argument_group('Filter processes')
    g.add_argument('PATTERN', nargs='*', type=str, help='process cmdline, better use after --')
    g.add_argument('-m', '--mode', default='any', choices=['any', 'start', 'full'], type=str, help=f'How to check PATTERN process (see below)')
    g.add_argument('-a', '--age', type=str, metavar='AGE', default=def_time, help=f'show processes with age higher then AGE. Example: 1h30m default: {def_time})')
    g.add_argument('-e', '--exe', metavar='PATH', type=str, help=f'only this executable')
    g.add_argument('-u', '--user', default=None, type=str, help=f'username of process')

    g = parser.add_argument_group('Action with processes')
    g.add_argument('--kill', action='store_true', default=False, help=f'Brutally kill it with SIGKILL (like kill -9)!')
    g.add_argument('--terminate', action='store_true', default=False, help=f'Gracefully terminate with SIGTERM')

    g = parser.add_argument_group('Another options')
    g.add_argument('-j','--json', action='store_true', default=False, help=f'Output as JSON')

    parser.epilog = """
How to use pattern matching\n---\n
Suppose we are looking for "ssh -i ~/.ssh/my_key.pub my.host.name"

any: each word from PATTERN must be found somewhere in cmdline (default mode). Examples:
dieyoung -a 1h -- ssh -i 
dieyoung -a 1h -- -i ssh
dieyoung -a 1h -- ssh my.host.name 
dieyoung -a 1h -- my.host.name

start: cmdline must start with PATTERN, but may contain additional words. Example: dieyoung -- ssh -i

full: cmdline must be fully equal to PATTERN
    """
    return parser.parse_args()

def print_process(p: psutil.Process):
    age = int(time.time() - p.create_time())

    if args.json:
        data = {
            'pid': p.pid,
            'exe': p.exe(),
            'name': p.name(),
            'started': int(p.create_time()),
            'age': seconds2human(age),
            'cmdline': p.cmdline(),
            'username': p.username()
        }
        rich.print(data)
    else:
        rich.print(f'{p.pid} [red]{seconds2human(age)}[/red] {" ".join(p.cmdline())}')

def process_match(p: psutil.Process, args: argparse.Namespace):

    # Never return myself
    if p.pid == os.getpid():
        return False

    # --exe
    if args.exe and p.exe() != args.exe:
        return False

    # time
    age = int(time.time() - p.create_time())
    if age < max_age:
        return False

    # user
    if args.user and p.username() != args.user:
        return False

    if args.mode == 'any':
        if all(arg in p.cmdline() for arg in args.PATTERN):
            return True
    elif args.mode == 'start':    
        if p.cmdline()[:len(args.PATTERN)] == args.PATTERN:
            return True
    elif args.mode == 'full':
        if p.cmdline() == args.PATTERN:
            return True


    return False

def main():
    global args, max_age
    args = get_args()
    max_age = human2seconds(args.age)

    for p in psutil.process_iter():
        try:
            pid = p.pid
        # skip other processes
            if not process_match(p, args):
                continue
            age = int(time.time() - p.create_time())
            print_process(p)            
            if args.terminate:
                p.terminate()
                p.wait()
                print(f"terminated {pid}!")
            elif args.kill:
                p.kill()
                p.wait()
                print(f"killed {pid}!")
        except psutil.AccessDenied:
            pass
