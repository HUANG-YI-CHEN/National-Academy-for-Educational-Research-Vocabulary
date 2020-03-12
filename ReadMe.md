# National Academy for Educational Research Vocabulary
Fetch Vocabulary from National Academy for Educational Research

# Getting Started
## Installation Environment
* Microsoft Windows`+`

## System Requirements
* Python `3+`

## Mounting Kit  
* pip freeze > requirements.txt (Output installed packages in requirements)
```
pip install -r requirements.txt
```

## Execute Program
```
python main.py
```
or

```
python main.py 1 0 1000
```
## Constructor
* cur_page = '', <type 'int'>, get crawler page index
* page = '', <type 'int'>, get naer total page by each of 50 row page .
* result = [], <type 'list'>, get naer result lists.
* proxy_switch = False, <type 'boolean'>, input True or False.

## Fuction

## Example
```
nv = naer()
print(nv.result)
```

## Configuration File
Establish configuration file(`config.ini`), which is placed under this project directory
* `config.ini` is following :
    *   [database]
        *   hostname=localhost
        *   username=
        *   password=
        *   database=

    *   [control]
        *   debug=1 # 1: display ; 0: no display
        *   indexpage=1 # intial, and it will change by crawler running

## Subsequent Settlement
To be continued ......