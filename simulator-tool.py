#!/usr/bin/python3
from subprocess import PIPE, CalledProcessError, Popen, TimeoutExpired
from subprocess import run as sub_run
import logging
import os
import shutil
import shlex
import signal
from concurrent.futures import ThreadPoolExecutor, wait

try:
    import click
except ImportError as e:
    if 'No module named \'click\'' in e.msg:
        sub_run('sudo pip3 install click'.split(), check=True)
        import click
    else:
        raise ImportError('Something other than a missing module is wrong: {}'.format(e.msg))


logging.basicConfig(format='[%(asctime)s]\t%(levelname)s: %(message)s')


def install_gazebo(log):
    '''Installs the latest version of Gazebo. Note: Only Ubuntu is officially supported.'''
    log.info('Installing Gazebo')
    # These commands are taken from the official Ubuntu install sequence
    # at http://gazebosim.org/tutorials?tut=install_ubuntu&cat=install
    install_commands = [
            'sudo sh -c \'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable\
 `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list\'',
            'wget http://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -',
            'sudo apt-get update',
            'sudo apt-get install gazebo7 libgazebo7-dev'
            ]
    for command in install_commands:
        # Yes, running in a shell has security concerns. It should be OK for this instance,
        # though - no non-hardcoded commands running, and it's easier than setting up the
        # necessary pipes and such
        sub_run(command, shell=True, check=True)
    log.info('Gazebo has been successfully installed!')


def download_assignment(log, assignment_name):
    '''Downloads and extracts the provided files for the given assignment'''
    url = 'https://rpal.cs.cornell.edu/teaching/foundations/assignments/' + assignment_name
    base_cmd = 'wget ' + url
    log.info('Downloading and extracting archive for {}'.format(assignment_name))
    def unzip(f):
        if not f.exception():
            sub_run('tar xzvf {}.tar.gz -C {}'.format(assignment_name, assignment_name).split())
        else:
            raise f.exception()

    with ThreadPoolExecutor(max_workers=1) as e:
        download_future = e.submit(lambda: sub_run(('wget ' + url + '.tar.gz').split(), check=True))
        download_future.add_done_callback(unzip)
    log.info('Downloading version signature for {}'.format(assignment_name))
    sub_run(('wget -O .sigs/{} ' + url + '.sig').format(assignment_name).split(), check=True)
    wait([download_future])
    log.info('Done downloading and extracting materials for {}'.format(assignment_name))


def remove_assignment(log, assignment_name):
    log.info('Deleting old assignment archive and directory')
    shutil.rmtree(assignment_name)
    os.remove('{}.tar.gz'.format(assignment_name))


def fetch_assignment(log, assignment_name):
    '''Fetch the most up-to-date version of the assignment specified'''
    url_format = 'https://rpal.cs.cornell.edu/teaching/foundations/assignments/{}.sig'
    # Check if assignment has already been fetched and is up to date
    if os.path.isdir(assignment_name):
        log.info('Found directory for {}'.format(assignment_name))
        log.info('Checking version signature for {}'.format(assignment_name))
        current_sig = sub_run(
                'wget -qO- {}'.format(url_format.format(assignment_name)).split(),
                stdout=PIPE,
                universal_newlines=True,
                check=True
                ).stdout
        with open('.sigs/{}'.format(assignment_name, assignment_name), 'r') as sigfile:
            old_sig = sigfile.readline()
        if old_sig != current_sig:
            log.info('Version of {} appears to be outdated. Downloading current version.'
                     .format(assignment_name))
            remove_assignment(log, assignment_name)
            os.mkdir(assignment_name)
            download_assignment(log, assignment_name)
        else:
            log.info('Version of {} is up to date; proceeding'.format(assignment_name))
    else:
        log.info('Found no existing files for {}. Downloading current version.'
                 .format(assignment_name))
        os.mkdir(assignment_name)
        if not os.path.isdir('.sigs'):
            os.mkdir('.sigs')
        download_assignment(log, assignment_name)


def build_assignment(log, assignment_name):
    # TODO: This seems unnecessary 
    def ensure_dir(dirname):
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
    curr_dir = os.getcwd()
    log.info('Moving into assignment directory')
    os.chdir(assignment_name)
    log.info('Ensuring existence of build directory')
    ensure_dir('build')
    os.chdir('build')
    if not os.path.isfile('Makefile'):
        log.info('No Makefile; running CMake')
        sub_run('cmake ..'.split(), check=True)
    log.info('Running make')
    sub_run('make', check=True)
    os.chdir(curr_dir)
    log.info('Building done. {} is ready to run'.format(assignment_name))


def run_gazebo(log, assignment_name, problem):
    log.info('Running test driver for {}'.format(assignment_name))
    driver_proc = Popen(
            '{}/build/{}'.format(assignment_name, problem),
            stdin=None,
            stdout=None,
            stderr=None
            )
    env  = os.environ.copy()
    env['GAZEBO_PLUGIN_PATH'] = '{}/{}/build/'.format(os.getcwd(), assignment_name)
    env['GAZEBO_MODEL_PATH'] = '{}/{}/models/'.format(os.getcwd(), assignment_name)
    log.info('Running gazebo with the world for {}'.format(assignment_name))
    gazebo_proc = Popen(
            shlex.split('gazebo --verbose {}/{}.world'.format(assignment_name, assignment_name)),
            stdin=None,
            stdout=None,
            stderr=None,
            env=env
        )
    # Run for 60 seconds max
    try:
        driver_proc.wait(timeout=60)
    except TimeoutExpired:
        os.killpg(os.getpgid(driver_proc.pid), signal.SIGTERM)
    log.info('Wrapping up execution...')
    os.killpg(os.getpgid(gazebo_proc.pid), signal.SIGTERM)
    log.info('Done with execution')


@click.group()
def cli():
    pass


# TODO: Add no-check option
@cli.command()
@click.argument('assignment')
@click.argument('problem')
def run(assignment, problem):
    '''Build (if necessary) and run the given assignment problem.'''
    log = logging.getLogger('simulator-run')
    log.setLevel(logging.INFO)
    fetch_assignment(log, assignment)
    build_assignment(log, assignment)
    run_gazebo(log, assignment, problem)


@cli.command()
def install():
    '''Install Gazebo'''
    log = logging.getLogger('simulator-install')
    log.setLevel(logging.INFO)
    log.info('Checking to see if we already have gazebo')
    if shutil.which('gazebo'):
        log.info('Gazebo is already installed! Exiting.')
        return
    else:
        log.info("Gazebo doesn't seem to be installed.")
        install_gazebo(log)


# TODO: Add no-check option
@cli.command()
@click.argument('assignment')
def build(assignment):
    '''Build the given assignment'''
    log = logging.getLogger('simulator-build')
    log.setLevel(logging.INFO)
    fetch_assignment(log, assignment)
    build_assignment(log, assignment)


@cli.command()
@click.argument('assignment')
def get(assignment):
    '''Download the given assignment'''
    log = logging.getLogger('simulator-get')
    log.setLevel(logging.INFO)
    fetch_assignment(log, assignment)


if __name__ == '__main__':
    cli()
