# CMPE133-TaskMate

## Instructions to run the project in the Terminal app:

### Download and locate project directory
1. Download the project source code from Github, and keep in mind where the directory was downloaded to on your system

2. Open a new Terminal app window on your system

3. Navigate to the project directory in Terminal

Mac/Linux & Windows (the path after "cd" will depend on which directory your system downloads to and the name of the directory)
```
cd Downloads/CMPE133-TaskMate-main
```

### Install the dependencies
1. Create a virtual environment in your project directory

Mac/Linux & Windows
```
python3 -m venv venv
```


2. Activate virtual environment. In your project directory:

Mac/Linux on bash/zrc
```
$ source venv/bin/activate
```

Windows on cmd.exe
```
C:\> venv\Scripts\activate.bat
```

Windows on PowerShell
```
PS C:\> venv\Scripts\Activate.ps1
```

3. Install all requirements
```
pip install -r requirements.txt
```

### Run project
```
python3 run.py
```
