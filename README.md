# SDLE Project

SDLE Project for group T1G16.

Group members:

1. André Gomes (up201806224@edu.fe.up.pt)
2. Daniel Silva (up201806524@edu.fe.up.pt)
3. Luís Marques (up201104354@edu.fe.up.pt)
4. Rodrigo Reis (up201806534@edu.fe.up.pt)

## Set Up

1. Install miniconda or anaconda via the following link: <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>
2. clone this repository
3. In the root of this project, create a conda environment from the `environment.yml` file:

```bash
conda env create -f environment.yml
```

4. Activate the environment

```bash
conda activate sdle_p1
```

## Run

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

## Demonstrations

> No relatório como na demonstração deverão focar-se nas garantias de fiabilidade do serviço. Na demonstração deverão demonstrar a durabilidade das subscrições e a tolerância a falhas relativamente simples, p.ex. "crash" do servidor ou dum subscritor. Cenários de falhas mais complexos, p. ex. que envolvam mensagens de "acknowledgement", deverão ser discutidos no relatório.

### Demo 0 - Test iteratively

Use the flag `dev` to test anything using the nodes

- Delete `proxy.pickle` file and run server
- Run any number of nodes with diferent `ID`'s using `python3 src/node.py <Node_ID> dev`

### Demo 0 - Normal functioning

- Sub -> Put -> Get -> Unsub
- Sub -> Get -> Put -> Unsub
- SUB -> Put -> Put -> Get -> Get -> Unsub

### Demo 1 - Subscription Durability

A sub subscribes and waits for messages to be put in the topic. A publisher puts some messages in the topic and exits. The subscriber gets 1 of the messages and exits. The proxy can be restarted and the state is mantained.

Server-side:

- Delete `proxy.pickle` file and run server
- Run node as `SUB1 dev` and run node as `PUB1 dev`
- Sub -> Put -> ProxyCrash -> ProxyUp -> Get

client-side:

- Delete `proxy.pickle` file and run server
- Run node as `SUB1 dev` and run node as `PUB1 dev`
- Sub -> Put -> SubCrash -> SubUp -> Get

### Demo 2 - Crashing while Waiting GET

- Delete `proxy.pickle` file and run server
- Run node as `SUB1 dev` and run node as `PUB1 dev`
- Sub -> Get -> SubCrash -> SubUp -> Put -> Get
- Sub -> Get -> SubCrash -> Put -> SubUp -> Get


## Conda commands

- `conda activate sdle_p1` - to activate the environment
- `conda env export --from-history > environment.yml` - to export environment to a configuration file
- `conda env create -f environment.yml` - to create an environment from a configuration file
- `conda install --name sdle_p1 package-name` - to install packages
