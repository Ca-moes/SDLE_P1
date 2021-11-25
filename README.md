# SDLE Project

SDLE Project for group T1G16.

Group members:

1. André Gomes (up201806224@edu.fe.up.pt)
2. Daniel Silva (up201806524@edu.fe.up.pt)
3. Luís Marques (up201104354@edu.fe.up.pt)
4. Rodrigo Reis (up201806534@edu.fe.up.pt)

# Set Up

1. Install miniconda or anaconda via the following link: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
2. clone this repository
3. In the root of this project, create a conda environment from the `environment.yml` file:
```bash
conda env create -f environment.yml
```
4. Activate the environment
```bash
conda activate sdle_p1
```

# Run

1. Initiate the Proxy
```bash
python3 src/proxy.py
```
2. Initiate Nodes
```bash
python3 src/node.py <Node_ID> [dev]
```
- If the `dev` flag is activated, the user will be granted a iterative prompt to send messages. PLease follow the requested syntax carefully, in this mode, topics and messages submitted can not have more than one word (if necessary, use `_` to separate words)
- if the `dev` flag is not activated, the node will run steps according to its source code, the steps are in the following format:
```python
if identity == '<Node_ID_1>'
  <Steps>
elif identity == '<Node_ID_2>'
  <Steps>
```
A Step could be any of the following:
```python
time.sleep(<seconds>)
sub(socket, [<Topic>])
unsub(socket, [<Topic>])
get(socket, [<Topic>])
put(socket, [<Topic>, <Message>])
```
This way, it is possible to have Topics and Messages with multiple words

# Conda commands

- `conda activate sdle_p1` - to activate the environment
- `conda env export --from-history > environment.yml` - to export environment to a configuration file
- `conda env create -f environment.yml` - to create an environment from a configuration file
- `conda install --name sdle_p1 package-name` - to install packages 
