# Shot

**S**creenshot  
**H**elper for  
**O**SX  
**T**erminal 

# Install

# Example
```bash
# default is to copy the latest screenshot to the current directory
shot

# copy the last 3 screenshots to ./foo
shot --dest=./foo --n=3

# move the second last screenshot to ./bar
shot --cmd=mv --dest=./bar --s=2

# output the command shot would run
shot --cmd=something_that_does_not_exist --dry_run
```