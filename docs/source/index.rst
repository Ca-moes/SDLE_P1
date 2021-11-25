.. Tutorial on Documentation using Sphinx documentation master file, created by
   sphinx-quickstart on Sun Jun 17 16:23:30 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Configuration of Project Environment
*************************************

This Project is composed of 2 programs: A Node and a Proxy. The Node communicates via the Proxy to subscribe to topics and send messages.

Overview on How to Run this Project
===================================
1. Install anaconda or miniconda
2. Create a conda environment from requirements
3. Run 

Setup procedure
================
1. Configure project environment with conda
  - Install anaconda or miniconda

  - Create environment::

      conda env create -f environment.yml
  
  - Activate the environment::

      conda activate sdle_p1

2. Initiate proxy::

    python3 src/proxy.py

3. Initiate Nodes
  A. Nodes can simultaneously be Publishers and Subscribers, and are initiated in the following manner::

      python3 src/node <Node_ID> [dev]

  - <Node_ID> Each node needs an identifier
  - [dev] A Node can start in a development state. In the development state, the node waits for input to determine the type of message to send. Out of development state, the note follows a set of instructions detailed in the source code, subject to change.


Documentation for the Code
**************************
.. toctree::
   :maxdepth: 2
   :caption: Contents:

Utils
=================
.. automodule:: src.utils
   :members:

Proxy
=====================
.. automodule:: src.proxy
   :members:

Node
=================
.. automodule:: src.node
   :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
