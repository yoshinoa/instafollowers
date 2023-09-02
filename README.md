# instafollowers

instagram data aggregation

# installation

## pipenv

run `pipenv install`

## pip

run `pip install -r requirements.txt`

# setup

it looks like instaloader setup is no longer working, to setup, log into instagram through the firefox browser, then run the program with the -s flag.

# usage

usage:

```
main.py [-h] [-s] -u USERNAME [-p PASSWORD] [-t TARGET] [-o OUTPUT] [-c COMPARE]
[-l LOCAL] [-date] [-n OMIT]
```

Perform analysis on instagram accounts.

optional arguments:

`-h`, `--help` show this help message and exit

`-s`, `--setup` Run with -s to setup authorization.

`-u USERNAME`, `--username USERNAME`
Set the username to run with. (i.e. the username you will scrape with)

`-p PASSWORD`, `--password PASSWORD`
Set the password to run with.

`-t TARGET`, `--target TARGET`
Set the target to run against. (i.e. the user you are scraping)

`-o OUTPUT`, `--output OUTPUT`
Set the output file to write to.

`-c COMPARE`, `--compare COMPARE`
Compare an old pickle to a new username, input the revision
number or 0 for no revision number

`-l LOCAL`, `--local LOCAL`
Load a pickle file, same scheme as compare instead of getting current version

`-date`, `--date` Check the dates of the pickle files currently stored

`-n OMIT`, `--omit OMIT` feature that has not been implemented
