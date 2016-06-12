## Install

This project requires Redis for the caching of scanned devices. The rest of the dependencies are found in the `setup.py`.

```
pip install -e .
sudo apt-get install redis-server
```

## Settings
You should create your own setting.ini to run with by copying the settings.ini.dist and assigning values to the given keys.
```
cp settings.ini.dist settings.ini
```

## Run
You can run the project by doing
```
python -m smartgympi.client
```
