import logging
logger = logging.getLogger(__name__)
f_handler = logging.FileHandler('/home/pi/password-store-commit.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)

import sys
from git import Repo
import os
import shutil

def print_commit_details(commit):
    logger.info("---------------")
    logger.info("Commit SHA256: {} ".format(str(commit.hexsha)))
    logger.info("Commit Summary: {} ".format(commit.summary))
    logger.info("Commit Datetime: {} ".format(commit.authored_datetime))


def check_files_directories(path):
    result = False

    if os.path.exists(path):        
        result = True
        return result
    else:
        logger.info("The path {} does not exists, please check the script ".format(path))

    return result


def cleanup_tmp(path):

    if check_files_directories(path):
        logger.info("Removing the checked out remote repo in /tmp directory")        
        shutil.rmtree(path)
        logger.info("Deletion successful... ")


def main():

    WORKING_PATH = "/home/pi/.password-store"
    # cloning the remote repository via SSH (You public keys for this host should be present on github)
    remoteUrl = "git@github.com:your_repository/repo.git"
    remote_checkout_path = "/tmp/remote_repo"
    # checking and deleting the /tmp/remote_repo if that already exists for clean checkout
    if check_files_directories(remote_checkout_path):
        cleanup_tmp(remote_checkout_path)

    logger.info("Current working Repository Directory {} ".format(WORKING_PATH))
    logger.info("Remote URL to be checkout at {} is {} ".format(
        remote_checkout_path, remoteUrl))

    wrepo = ''
    if check_files_directories(WORKING_PATH):        
        wrepo = Repo(WORKING_PATH)        

    # checking out remote repository in /tmp for comparision
    remote_repo = Repo.clone_from(remoteUrl, remote_checkout_path)
    rrepo = Repo(remote_checkout_path)

    wrepo_commits = list(wrepo.iter_commits('master'))
    wrepo_commits_length = len(wrepo_commits)
    rrepo_commits_length = len(list(rrepo.iter_commits('master')))

    if rrepo_commits_length < wrepo_commits_length:
        diff_count = wrepo_commits_length - rrepo_commits_length
        logger("Found new {} commits in working directory, Rebasing the local directory".format(diff_count))
        try:
            # Rebase the current local repository
            if wrepo.remotes.origin.pull(rebase=True):
                logger.info("Rebase successfully Done")
        except Exception:
            logger.exception("Unable to rebase the repository, please check")
            sys.exit(1)
        logger.info("Pushing following commits: ")
        all_new_commits = wrepo_commits[:diff_count]
        if diff_count > 1:
            for commit in all_new_commits:
                print_commit_details(commit)
        else:
            print_commit_details(all_new_commits[0])

        # push changes
        try:
            if wrepo.remotes.origin.push():
                logger.info("Push is Successful ")
            else:
                logger.error("Some issues with push, check manually")
        except Exception:
            logger.exception("Issues while pushing the changes to remote master, Please check")

    else:
        logger.info("There are no changes in the directory, exiting the script")
        sys.exit(0)
    
    # Cleaning up the remote file
    cleanup_tmp(remote_checkout_path)


if __name__ == "__main__":
    main()
