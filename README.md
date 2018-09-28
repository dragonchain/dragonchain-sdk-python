# Dragonchain SDK

## Intro

This is the Python 3 SDK for interacting with a dragonchain.
It provides functionality to be able to interact with a dragonchain through a simple sdk with minimal configuration needed.

## Installation

!!!PyPi installation with pip TBD when uploaded!!!

You can also install this package from source. To do so, simply get the source code (via git clone like `git clone https://github.com/dragonchain-inc/dragonchain-sdk-python.git` or simply downloading/extracting a source tarball from releases), then navigate into the root project directory, then run:

    ./run.sh build
    sudo ./run.sh install

## Configuration

In order to use this SDK, you need to have an Auth Key as well as an Auth Key ID for a given dragonchain. This can be loaded into the sdk in various ways.

1. The environment variables `DRAGONCHAIN_AUTH_KEY` and `DRAGONCHAIN_AUTH_KEY_ID` can be set with the appropriate values
2. The `dc_sdk.client` can be initialized with `auth_key=<KEY>` and `auth_key_id=<KEY_ID>`
3. Write an ini-style credentials file at `~/.dragonchain/credentials` where the section name is the dragonchain id, with values for `auth_key` and `auth_key_id` like so:

    ```ini
    [35a7371c-a20a-4830-9a59-5d654fcd0a4a]
    auth_key_id = JSDMWFUJDVTC
    auth_key = n3hlldsFxFdP2De0yMu6A4MFRh1HGzFvn6rJ0ICZzkE
    ```

## Usage

After installation, simply import the sdk and initialize a client object with a dragonchain ID to get started.
An example of getting a chain's status is shown below:

```python
import dc_sdk

client = dc_sdk.client(id='DRAGONCHAIN ID HERE',
                       auth_key='OPTIONAL AUTH KEY IF NOT CONFIGURED ELSEWHERE',
                       auth_key_id='OPTIONAL AUTH KEY ID IF NOT CONFIGURED ELSEWHERE')

client.get_status()
```
