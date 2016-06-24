# Prophessor
Phabricator Assessessments Automation

# Dependencies

- Python ~2.7
- Arcanist

# Introduction

This is a software package designed to automate some specific tasks related to using Phabricator as a teaching aid.

This package is biased towards and designed for lectures by Luke Anderson.

# Usage

Commands are executed by running `proph.py` from Python with arguments.

For example:
```
$python proph.py enroll students.csv
```

This script uses a variety of methods to communicate with Phabricator:

- Arcanist
- Phabricator RESTful API
- Phabricator PHP files
- Direct access to the Phabricator SQL database.

Some of the above mentioned methods are able to be run remotely and others must be run from the Phabricator server.
The most fail-safe way to run this script is on the Phabricator server, all functions will are supported when run
directly on the Phabricator server with access to the Phab db, Phab PHP files, Arcanist and the RESTful API.

Some configuration is required for each Phabricator instance. All of these settings are available in the
`local_settings.py` file.

# Commands


## enroll

```
$ python proph.py enroll <csv file>
```

_Utilises Phabricator PHP files and must be executed on the Phabricator server_

Creates users based on the information in the specified `<csv file>`.

See `example_files/students.csv` for an example of the `<csv file>`.

Example: `$ python proph.py enroll example_files/students.csv`


## create-projects

```
$ python proph.py create-student-groups <csv file> <project number>
```

_Implements the RESTful API and may be run remotely_

Create Phab student projects and assigns users to these projects as per the specified `<csv file>`.

`<project number>` is a number which will be appended to the project name to accommodate for multiple projects per Phabricator instance.

See `example_files/students.csv` for an example of the `<csv file>`.

Example: `$ python proph.py create-student-groups example_files/students.csv 1`


## create-marker-groups

```
$ python proph.py create-marker-groups <csv file> <project number>
```

_Implements the RESTful API and may be run remotely_

Create Phab marking projects and assigns users to these projects as per the specified `<csv file>`.

`<project number>` is a number which will be appended to the project name to accommodate for multiple projects per Phabricator instance.

See `example_files/markers.csv` for an example of the `<csv file>`.

Example: `$ python proph.py create-marker-groups example_files/markers.csv 1`


## load-diffs

```
$ python proph.py load-diffs <directory of diffs> <project number>
```

_Requires Arcanist and access to the Phabricator database_

Import all git diff files with `.diff` extension from the `<directory of diffs>` directory and perform the following actions for each file:

- Create a Differential
- Create a Differential Revision
- Determine the group number from the `.diff` filename and give view and edit permissions for the Revision
to the marking group which matches the group number and `<project number>` specified.

See `example_files/diffs` for an example of the directory and `.diff` files.

Example: `$ python proph.py load-diffs example_files/diffs/ 1`

# Notes

## Students & markers CSV file

The format of this file is the same as the one downloaded from Blackboard, however you will need to add an "Email" column
and a "Password" column. You can use random.org to generate the passwords and easily paste them into Excel (or similar).

## Diffs

One of the git diffs I faced was in UTF-16-LE encoding and Phabricator didn't like this. I used the ubiquitous `iconv`
program (Linux/Unix/OSX) to convert the file to UTF-8 which Phabricator then accepted.


# Credits

Concept and original design by Luke Anderson

Re-factor by Paul Hauner.