# Python program example for the iRIC private solver


## main.py
This file is the python program example for the iRIC private solver.

## definition.xml
This file defines the input data interface for the iRIC software.

## Case1.cgn
This file is the samle data for the mysolver.


# How to execute 

Execute command is as follow.

```
> python main.py ./sample_data/case1.cgn
```

So add followings into the "launch.json" if you would like to run this solver on the Visual Studio Code. Example for the "launch.json" is in the ".vscode" directory.

```
"args": ["./sample_data/Case1.cgn"],
```
