# rotools

## Watch

Will sit and watch the branch you're working on and make a sound when CI is
complete.

### Installing

1. create a virtual environment
2. `pip install --upgrade pip setuptools wheel`
3. `pip install -r requirements.txt`

### Configure

Needs a yaml file in running directory named `config.yaml`

```yaml
---
github_token: <token from github>
sound: elegant-notification-sound.mp3
```

### Running

`python watch.py /PATH/TO/REPO`

### Getting token from github

1. Log into github
2. Click your top-right user icon
3. Click `Settings`
4. Click `Developer settings` at bottom of left navigation
5. Click `Personal access tokens`
6. Click `Tokens (classic)`
7. Generate a new token and copy it
8. Paste token into config
9. Click `Configure SSO` on that token and do the things

### Known issues

If the remote branch gets deleted it'll error, but just restart it
