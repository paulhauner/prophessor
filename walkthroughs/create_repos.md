# How to complete Repository creation

This readme will walk you through the following:

- Setting a repository to be hosted on Phabricator
- Setting a repository's policies

### Assumptions

This guide is assuming you have already done the following things:

- Enrolled all your students into Phabricator using prohessor's `enroll` command with a `.csv` of your student users.
- Created all your groups in Phabricator using prophessor's `create-student-groups` command.
- Created all your repositories in Phabricator using prophessor's `create-repos` command with a `.csv` of your student users.

## Walkthrough

All of the following steps need to be taken through the Phabricator website using an Administrator's account.

#### 1. Hosting on Phabricator

For each repository, you will need to press "Edit Repository", then navigate down to "Hosting". You will then need to edit the "Hosting" settings to "Host Repository on Phabricator".

The rest of the settings under "Hosting" may be left untouched.

#### 2. Repository Policies

For each repository, you will need to press "Edit Repository", then navigate down to "Policies". You will then need to edit each of the "Policies" settings to "Members of Project: X", where X is the Project that should have access to this repository.

#### 3. ....

#### 4. Profit

You should be done now! Each repository should be set up correctly and can only be viewed by the relevant Project.
