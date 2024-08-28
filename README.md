# dieyoung
Find / kill very long running processes by name, args and age

## Installation
recommended way:
`pipx install dieyoung`

or (better if inside python virtualenv):
`pip install dieyoung`
your system may have `pip3` instead of `pip`.

## Find processes by name / arguments, three different modes
See all my ssh sessions:
~~~shell
$ dieyoung ssh
732333 8h ssh alv
742297 7h ssh jul
745335 6h ssh mx
875490 38m ssh -i /home/xenon/.ssh/id_ed25519 mx
880910 25m ssh mx -i /home/xenon/.ssh/id_ed25519
~~~
Format is simple: pid, age, cmdline

Now, lets suppose we want to find only ssh to mx:
~~~shell
$ dieyoung ssh mx
745335 6h ssh mx
875490 39m ssh -i /home/xenon/.ssh/id_ed25519 mx
880910 25m ssh mx -i /home/xenon/.ssh/id_ed25519
~~~
Three sessions are found, because each of them has "ssh" and "mx" in cmdline (in any order). This is how `--mode any` (default mode), process matches our pattern if all words from pattern are found *anywhere* in process cmdline, even if there are other arguments.

`--mode start`: First words of cmdline must match pattern, e.g. 
~~~shell
$ dieyoung -m start -- ssh -i 
875490 39m ssh -i /home/xenon/.ssh/id_ed25519 mx
~~~
But this filter will not find process `ssh mx -i /home/xenon/.ssh/id_ed25519` (because `ssh mx` is not `ssh -i`). 
Note, we used `--` to separate PATTERN (`ssh -i`) from dieyoung arguments.

`--mode full`: process cmdline must fully match pattern, e.g.
~~~shell
$ dieyoung -m full -- ssh -i /home/xenon/.ssh/id_ed25519 mx
875490 40m ssh -i /home/xenon/.ssh/id_ed25519 mx
~~~

## Filter by age, user and executable
To find processes older then some age use `-a` / `--age` option, like `-a 1h30m` (to find processes older then 1 hour and 30minutes)

`--exe PATH` to find only processes with this executable, e.g. if you want to find `/usr/bin/php` but not `/opt/php/7.4/bin/php`.

`--user USERNAME` to find only processes of this user. 


## Kill / Terminate processes
After you found processes, you may kill it manually with `kill` command, or use built-in feature. Add `--terminate` option to gracefully send SIGTERM to each matching process or `--kill` to send `SIGKILL` (like `kill -9 <pid>`).

## Inspect more details of processes
Add `-j` / `--json` to show more info about processes



