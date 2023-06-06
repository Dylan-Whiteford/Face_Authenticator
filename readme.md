# Face Authenticator


## Env
### Reqirements
- python3.9

```````
    $ git clone https://github.com/Dylan-Whiteford/Face_Authenticator.git    
    $ python39 -m venv env
    $ source env/bin/activate
    $ python39 -m pip install -r requirements
```````

- This projecct is run in a python3.9 virtual environment
- There is a mongodb docker container that is used as the database
- flask was used to create a simple api
- pyscript was used in tandem with html to make a simple webclient(incomplete)


## Running
### Start Mongodb
```````
    $ ./DB/run 
```````

### Start Recorder
```````
    $ python39 Face_Image_Generator/recorder.py 
```````

