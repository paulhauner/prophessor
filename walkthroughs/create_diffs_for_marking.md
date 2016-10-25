# How to generate diffs for marking

This readme will walk you through the following:

- Creating the Phabricator groups used for marking the project.
- Creating diff files from Phabricator git repos.
- Loading the diff files into Phabricator as 'Differential' revisions and assigning them to the correct marking groups.

### Resources

The main [README.md](/README.md) aims to exhaustively specify all of the commands you can run with `prophessor`.
It is worth your time to read through it and understand what it's doing.

You should definitely read the info for the following commands:

- `create-marker-groups`
- `generate-diffs`
- `load-diffs`

### Assumptions

This guide is assuming you have already done the following things:

- Enrolled all your markers into Phabricator using prophessor's `enroll` command with a `.csv` of your student users.
- Created all your groups in Phabricator using prophessor's `create-student-groups` command.
- Enrolled all your markers into Phabricator using prophessor's `enroll` command with a `.csv` of your marker users.

### Server Setup

All of these commands need to be run on the same machine which hosts Phabricator (ie, where the PHP files are).

I, the author, use `docker` to host Phabricator, therefore I must use the `$ docker exec -it <container> /bin/bash` command to get an interactive shell on the Phabricator server in order to run `prophessor` commands.

Inside my `docker` container, I have a [shared volume](https://docs.docker.com/engine/tutorials/dockervolumes/#/mount-a-shared-storage-volume-as-a-data-volume) with my host at `/shared_volume`.
It is in this folder I store the `prophessor` repo and all related files (eg, csv files for students and markers and diff files). This is useful as sometimes I want to manipulate these files in the comfort of my host OS shell, instead of doing everything inside `docker`.

In the document, I am going to use my server setup in commands, hence why you will see the `/shared_volume` path in examples.

## Walkthrough

_Remember, everything needs to be done on the Phabricator server - for me, that's inside a docker container._

Make sure you pay attention to the output of the prophessor commands - they will tell you when things go wrong or it couldn't figure out who a diff belongs to.

#### Create Groups for Markers 

```
$ cd /shared_volume
$ python proph.py create-marker-groups /shared_volume/students.csv /shared_volume/markers.csv 69
```

_The '69' is the project number. Each time you have a sumbmission, it should have a unique project number. 69 is a silly number, for teh lols.
Eg. if you have a mid-semester submission and a final end-of-semester submission, use project number '1' for the mid-semester submission and project number '2' for the end-of-semester submission._

_The students file is our source of truth for how many groups there are in this class._

_The markers file is used to allocate groups evenly and randomly (randomly-enough) between groups._

#### Generate Diffs

```
$ mkdir folder_for_my_diffs
$ python proph.py generate-diffs 2012-09-01 /var/repo /shared_volume/folder_for_my_diffs
```
_The folder you use for your diffs is arbitrary._

_The date is the cut off point for commits. You will get a diff between the very first commit and the last commit before this date._

_`/var/repo` is where Phabricator stores it's repositories. This is probably the same for you unless you set a different location._

#### Turn the Diff Files into Differential Revisions

_Be careful running this command, each time you run it you will generate new Differential Revisions. You only want to run this once to avoid getting duplicates._

```
$ python proph.py load-diffs /shared_volume/folder_for_my_diffs 69
```

_The '69' is the project number again. Make sure it matches the one you used in the `create-marker-groups` command earlier in this walkthrough._



