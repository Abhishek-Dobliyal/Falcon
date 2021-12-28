# Falcon
Remotely monitor any system through simple HTTP requests.

## Installations and Dependencies

- [Python](https://www.python.org) Installed.

- Open Terminal/ Command Prompt and type in:

-> Windows Users

```bash
pip install -r /path/to/requirements.txt
```

-> MacOS/Linux Users

```bash
pip3 install -r /path/to/requirements.txt
```

## Usage

- Inside the Repository's directory, Open Terminal/ Command Prompt and type in:

-> Windows Users

```bash
python app.py
```

-> MacOS/Linux Users

```bash
python3 app.py
```

- The above command should result in something like this:
```bash
 Debug mode: on
 * Running on http://192.168.1.x:XXXX/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
```

- Then run the [client.py]() on the system that is to be monitored with the following command:

-> Windows Users

```bash
python client.py
```

-> MacOS/Linux Users

```bash
python3 client.py
```

## Note

- Kindly do not move, delete, rename or modify any files (unless you know what you are doing).

- This is just a small scale implementation.
