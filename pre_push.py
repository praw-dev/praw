import shlex
import subprocess


def _exit():
    print('\nPlease fix and re-run to complete checks')
    exit(1)


def do_process(command):
    print(command)
    command = shlex.split(command)
    try:
        process = subprocess.Popen(command, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print('Command `%s` not found' % command[0])
        return 1
    error_level = process.wait()
    if error_level == 0:
        print('Good.\n')
    return error_level


if __name__ == '__main__':
    if do_process('flake8 --exclude=docs'):
        _exit()
    elif do_process('pydocstyle praw'):
        _exit()
    else:
        do_process('pylint --rcfile=./.pylintrc praw')
