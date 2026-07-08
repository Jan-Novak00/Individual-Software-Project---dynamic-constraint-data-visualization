# Individual-Software-Project---dynamic-constraint-data-visualization
## Structure
This repository contains source code for my project for NPRG045 and its extension for batchelor thesis.

Source files common for chart editor and for prediction game (constraint solving and UI management) can be found in [module](./module/src/kiwiplots/) directory.
Source files for chart editor can be found in [editable-plots](./editable-plots/) directory. Chart editor can be run by running [main](./editable-plots/main.py) file using python interpreter.

Extension for the prediction game can be found in [prediction-game](./prediction-game/) directory. This directory also contains [main](./prediction-game/main.py) script which runs the prediction game (run with your python interpreter).

## How to run
Clone the repository to your machine and run any of the two previously mentioned *main* scripts with your python interpreter. 

The only external dependency is the _kiwisolver_ library. You can install it using
```bash
pip install kiwisolver
```

## Prediction game examples
Prediction game examples can be found in directory [game examples]("./game examples/").
