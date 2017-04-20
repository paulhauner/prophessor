# Prophessor
Phabricator Assessessments Automation

## Dependencies

- Python ~2.7
- Arcanist

## Introduction

This is a software package designed to automate some specific tasks related to using Phabricator as a teaching aid.

This package is biased towards and designed for lectures by Luke Anderson.

I am have started writing walkthroughs to document the procedures for common actions:

- [Creating Diffs for Marking](/walkthroughs/create_diffs_for_marking.md)

## Usage

Commands are executed by running `proph.py` from Python with arguments.

For example:
```
$python proph.py enroll students.csv
```

This script uses a variety of methods to communicate with Phabricator:

- Arcanist
- Phabricator RESTful API
- Phabricator PHP files
- Direct access to the Phabricator SQL database

Some of the above mentioned methods are able to be run remotely and others must be run from the Phabricator server.
The most fail-safe way to run this script is on the Phabricator server, where all functions are supported, with access
to the Phab db, Phab PHP files, Arcanist and the RESTful API.

Some configuration is required for each Phabricator instance. All of these settings should be made available in
`local_settings.py`, which you will need to create. An example is provided in the
`example_files/example_local_settings.py` file.

## Commands




### enroll

```
$ python proph.py enroll <csv file>
```

_Utilises Phabricator PHP files and must be executed on the Phabricator server_

Creates users based on the information in the specified `<csv file>`.

See `example_files/students.csv` for an example of the `<csv file>`.

Example: `$ python proph.py enroll example_files/students.csv`






### create-student-groups

```
$ python proph.py create-student-groups <student csv file> <project number>
```

_Implements the RESTful API and may be run remotely_

**Before running this command you should have already created your student accounts (this can be done with `enroll`)**

Create Phab student projects and assigns users to these projects as per the specified `<csv file>`.

`<project number>` is a number which will be appended to the project name to accommodate for multiple projects per Phabricator instance.

See `example_files/students.csv` for an example of the `<csv file>`.

Example: `$ python proph.py create-student-groups example_files/students.csv 1`






### lockdown-student-groups

```
$ python proph.py lockdown-student-groups <student csv file> <project number>
```

_Executes SQL. Must be run in an environment with access to the Phabricator database._

**Before running this command you should have already created student projects**

Lock down the permissions for the groups in the `<csv file>`. Each group will have view, edit and join policies
restricted to only the project itself.

`<project number>` is a number which will be appended to the project name to accommodate for multiple projects per Phabricator instance.

See `example_files/students.csv` for an example of the `<csv file>`.

Example: `$ python proph.py lockdown-student-groups example_files/students.csv 1`






### create-marker-groups

```
$ python proph.py create-marker-groups <students csv file> <markers csv file> <project number>
```

_Implements the RESTful API and may be run remotely_

**Before running this command you should have already created your tutor accounts (this can be done with `enroll`)**

Create Phab marking projects and assigns tutors to these projects as per the specified csv files.

`<students csv file>` is used to get the list of groups.

`<markers csv file>` is used to get the list of tutors.

`<project number>` is a number which will be appended to the project name to accommodate for multiple projects per Phabricator instance.

See `example_files/markers.csv` for an example of the `<csv file>`.

Example: `$ python proph.py create-marker-groups example_files/markers.csv 1`






### create-repos

```
$ python proph.py create-repos <students csv file> <repo name>
```

_Requires API and access to docker container_

Create Phab repositories for each Group/Project as per the specified csv file.

`<students csv file>` is used to get the list of groups.

`<repo name>` is the name that all repositories will be given. Note that repositories will be unique based on their callsign.

See `example_files/students.csv` for an example of the `<students csv file>`

Example: `$ python proph.py create-repos example_files/students.csv Project`






### load-diffs

```
$ python proph.py load-diffs <directory of diffs> <project number>
```

_Requires Arcanist and access to the Phabricator database_

**Before running this command you should have already ran `create-marker-groups` and `create-student-groups` so the
differential revision policies can be effective**

Import all git diff files with `.diff` extension from the `<directory of diffs>` directory and perform the following actions for each file:

- Create a Differential
- Create a Differential Revision
- Determine the group number from the `.diff` filename and give view and edit permissions for the Revision
to the marking group which matches the group number and `<project number>` specified.

Determining the group number is handled by prophessor using one of the following methods:

 - Determine the group using a regex pattern from the file name.
 - Obtain a list of Diffusion 'callsigns' from Phabricator and check for filename matches
 to these callsigns.

See `example_files/diffs` for an example of the directory and `.diff` files.

Example: `$ python proph.py load-diffs example_files/diffs/ 1`



### grant-student-diff-access

```
$ python proph.py grant-student-diff-access <project number>
```

_Requires API and access to the Phabricator database_


Iterate through all Differential Revisions which match the project number. Matching is determined
by running a regex on the name of the Revision.

For each of the matching revisions, add a custom view policy which allows View and Edit permissions 
by both the students group and the markers group.

This is useful for when markers have finished marking Revisions and they would like the
students to have access to read comments and review.

Example: `$ python proph.py grant-student-diff-access 1`


### generate-diffs

```
$ python proph.py generate-diffs <final-submission-date> <phabricator repos dir> <dir to output diff files>
```

_Requires the RESTful API, Arcanist and access to the Phabricator database_

Scan the `<phabricator repos dir>` and attempt the following on each repository it finds:
 - Obtain the earliest commit on the `master` branch
 - Obtain the latest commit on the `master` branch _before_ the specified `<final submission date>`
 - Create a differential file inside the `<dir to output diff files>` with respect to the two commits mentioned above.

The `<phabricator repos dir>` is the folder in which Phabricator stores it's local repositories.
Historically, this folder is located at `/var/repo`.

The `<dir to output diff files>` is arbitrary.
You will most likely specify this folder as the `<directory of diffs>` folder when running the
`load-diffs` prophessor command.

The date should be specified in this format: `YYYY-MM-DD`

Example: `$ python proph.py generate-diffs 2016-09-27 /var/repo /shared_volume/diffs/`


## Notes

### Students & markers CSV file

The format of this file is the same as the one downloaded from Blackboard, however you will need to add an "Email" column
and a "Password" column. You can use [random.org](https://www.random.org/strings/) to generate the passwords and easily paste them into Excel (or similar).

### Diffs

One of the git diffs I faced was in UTF-16-LE encoding and Phabricator didn't like this. I used the ubiquitous `iconv`
program (Linux/Unix/OSX) to convert the file to UTF-8 which Phabricator then accepted.


## Credits

Concept and original design by Luke Anderson.

Re-factor by Paul Hauner.
