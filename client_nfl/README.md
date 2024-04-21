# Nillion Federated Learning Example

This is an example using the Nillion Python Client to store a program for federated learning.

## Assumptions

This multi-part Federated Learning example has the following assumptions:

- there is a global machine learning model with weight matrix `W`
- there are `N+1` parties (a server that stores the global model weights and `N` clients that computes local weights)
- each of the `N` clients contributes secret inputs of type SecretInteger, and allows the server to compute on the secret inputs
- the server stores the global weight matrix `W` (as public)
- the server runs compute
- the server party reads the output

Assume the training procedure lasts for `E` epochs.
This procedure is a multi-part procedure which contains the following steps:

1. the server shares the global weight matrix `W`
2. each of the `N` clients fetch the global matrix `W` and uses this to train one iteration of the model on the local data
3. each of the `N` clients updates the local weights as secret inputs.
4. the server uses each  of the `N` clients secret inputs to compute a new global weight matrix `W`
5. repeat steps 1-4 `E` times.

At the end of this procedure, we should obtain a global machine learning model that is obtained from combining the results
from `N` other parties which use local data only.

## Notes

This is a very naive and simple way of performing federated learning.
We are simply averaging the weights here at each iteration.
More advanced methods may be possible, but this is just a prototype of what is possible using Nillion.

## Run the example

1. Set up requirements following the repo README to populate the .env file with environment variables.

2. Follow README instructions to compile a program that meets the above assumptions. Take note of the program name. Here are some programs that meet the federated learning example program assumptions:

- nillion_federated_learning.nada.bin

```bash
cd ..
./compile_programs.sh
```

3. Update values in config.py to set the stored program name, party names, secret names, and secret values.

4. Start the example by running the following scripts.

- `01_initialize.py` - initializes the global model as well as splits the dataset among the given parties.
- `02_store_program.py` - stores the client under the global party (`server`)
- `03_train_and_upload.py` - trains each local model and uploads the weights as well as gives compute permissions to `server`
  - this script takes in an epoch parameter corresponding to when in the training process things are
- `04_compute_global_model.py` - aggregates the results of the local model privately by using the stored program. The output is then saved so that the local parties can update their version of the model.

Now you can repeat steps 3 - 4 for many epochs.

## Limitations

There are currently limitations regarding how many computations can be done in a specific program.
This limits the size of models and type of models that can be trained in a federated manner using Nillion.
However if the system can scale, then perhaps even LLM and models on medical data can have a real usecase here.
