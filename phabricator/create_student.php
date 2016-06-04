#!/usr/bin/env php
<?php
/**
 *
 *  This is an adaptation of phabricators bin/accountadmin script
 *  It will create a new phabricator user with settings appropriate for a student
 *
 *  This script assumes phabricator is installed in /opt/
 *
 *  This should be run from CLI and takes four arguments in the following order:
 *  username password realname email
 *
 *  Example:
 *      $ ./create_users.php "paramstest3" "phppassword" "Params3 Name3" "params3@dfadsfadf.com"
 *
 *  Author: paul@paulhauner.com
 *  Also contact: luke@lukeanderson.com.au
 *
 */
require_once '/opt/phabricator/scripts/__init_script__.php';
$table = new PhabricatorUser();
$any_user = queryfx_one(
  $table->establishConnection('r'),
  'SELECT * FROM %T LIMIT 1',
  $table->getTableName());
$is_first_user = (!$any_user);
if ($is_first_user) {
  echo pht('This would be phabricators first user. Cancelling')."\n";
  exit(1);
}


$username = $argv[1];
$realname = $argv[3];
$email = $argv[4];
$password = $argv[2];
$is_bot = False;
$set_admin = False;


//
// is username legit?
//
if (!PhabricatorUser::validateUsername($username)) {
  $valid = PhabricatorUser::describeValidUsername();
  echo pht("The username '%s' is invalid. %s", $username, $valid)."\n";
  exit(1);
}
$user = id(new PhabricatorUser())->loadOneWhere(
  'username = %s',
  $username);

//
// check if user exists
//
if($user) {
  echo pht("The username already exists")."\n";
  exit(0);
}
$user = new PhabricatorUser();
$user->setUsername($username);

//
// set name
//
$user->setRealName($realname);

//
// create email
//
$create_email = null;
do {
    $duplicate = id(new PhabricatorUserEmail())->loadOneWhere(
      'address = %s',
      $email);
    if ($duplicate) {
      echo pht(
        "ERROR: There is already a user with that email address. ".
        "Each user must have a unique email address.\n");
      exit(1);
    } else {
      break;
    }
} while (true);
$create_email = $email;

$user->openTransaction();
    $editor = new PhabricatorUserEditor();
    $editor->setActor($user);

    $email = id(new PhabricatorUserEmail())
      ->setAddress($create_email)
      ->setIsVerified(1);
    // Unconditionally approve new accounts created from the CLI.
    $user->setIsApproved(1);
    $editor->createNewUser($user, $email);

    $editor->makeAdminUser($user, $set_admin);
    $editor->makeSystemAgentUser($user, $is_bot);
    $envelope = new PhutilOpaqueEnvelope($password);
    $editor->changePassword($user, $envelope);
$user->saveTransaction();
