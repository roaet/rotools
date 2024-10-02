import signal
import sys
import time

from github import GithubException
from github import Github
from github import Auth
from git import Repo

from halo import Halo
from playsound import playsound
import yaml


complete_states = [
    'completed', 'cancelled', 'failure', 'skipped', 'stale', 'success',
    'timed_out', 'neutral'
]
incomplete_stats = [
    'queued', 'requested', 'waiting', 'pending', 'in_progress'
]

def get_workflow_data(remote, b, sha):
    ic = []
    cj = []
    wfs = remote.get_workflow_runs(branch=b, head_sha=sha)
    for wf in wfs:
        for j in wf.jobs():
            if j.status in complete_states:
                cj.append(j.name)
                continue
            ic.append(j.name)
    return ic, cj


def load_conf():
    with open("conf.yaml") as stream:
        try:
            conf = yaml.safe_load(stream)
            return conf
        except yaml.YAMLError as exc:
            print(exc)
    return None

def main():
    conf = load_conf()
    if conf is None:
        print("no conf")
        exit(1)

    auth = Auth.Token(conf.get('github_token', ""))
    if auth == "":
        print("github_token not found in conf")
        exit(1)
    sound = conf.get('sound', '')
    if sound == "":
        print("sound not found in conf")
        exit(1)

    repo = sys.argv[1]

    localRepo = Repo(repo)
    remote_url = localRepo.remote().url
    repo_name = ""
    if "git@github.com" in remote_url:
        remote_parts = remote_url.split(":")
        repo_name = remote_parts[1]

    g = Github(auth=auth)

    remoteRepo = g.get_repo(repo_name)

    if remoteRepo is None:
        print("Cannot find remoteRepo")
        exit(-1)

    branch = localRepo.active_branch.name
    old_branch = branch
    old_sha = ""
    spinner = Halo(text="initializing", spinner='dots')
    spinner.start()

    running = True
    def escape(sig, frame):
        spinner.stop()
        exit(0)

    signal.signal(signal.SIGINT, escape)

    def make_msg(branch, sha, msg):
        return f"{branch} ({sha}) - {msg}"

    spinner.text = make_msg(branch, '', "looking for commit")
    while running:
        try:
            # branch changed
            if old_branch != localRepo.active_branch.name:
                spinner.text = make_msg(branch, sha, "branch change")
                old_branch = localRepo.active_branch.name
                branch = old_branch

            # check for sha change
            b = remoteRepo.get_branch(branch)
            sha = b.commit.sha
            if old_sha == sha:
                # even if same sha check if workflows have happened
                ic, cj = get_workflow_data(remoteRepo, b, b.commit.sha)

                # no new workflows, sleep
                if len(ic) == 0:
                    time.sleep(10)
                    continue
                else:
                    spinner.text = make_msg(branch, sha, 'new workflow detected')
            else:
                spinner.text = make_msg(branch, sha, 'new commit detected')
            old_sha = sha
            # has been a change, wait a second then loop for changes
            time.sleep(10)

            complete = False
            initial = True
            while not complete:
                ic, cj = get_workflow_data(remoteRepo, b, b.commit.sha)
                if len(ic) == 0:
                    complete = True

                if not complete:
                    total = len(ic) + len(cj)
                    msg = "workflows not complete: {0}/{1}".format(len(ic), total)
                    spinner.text = make_msg(branch, sha, msg)
                else: 
                    # if initial loop probably don't need to output anything
                    if not initial:
                        playsound(sound)
                    spinner.text = make_msg(branch, sha, 'idling')
                    break
                initial = False
                time.sleep(10)
        except GithubException as e:
            print("github error: " % e)
            running = False
            continue
    spinner.stop()

if __name__ == "__main__":
    main()