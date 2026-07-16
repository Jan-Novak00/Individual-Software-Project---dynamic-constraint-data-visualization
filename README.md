# Individual-Software-Project---dynamic-constraint-data-visualization
## Structure
This repository contains source code for my project for NPRG045 and its extension for bachelor thesis.

Source files common for chart editor and for prediction game (constraint solving and UI management) can be found in [module](./module/src/kiwiplots/) directory.
Source files for chart editor can be found in [editable-plots](./editable-plots/) directory.
Extension for the prediction game can be found in [prediction-game](./prediction-game/) directory. 

## How to run
Clone the repository to your machine.
The program was debugged for Windows 10 and 11. On linux there might be problems with used fonts.
Make sure your machine has Python 3 interpreter installed, at least version 3.13.12.
You can run the **chart solver** by running **run-chart-editor.py** script in the root directory of the project.
**Prediction game** can also be run by running **run-prediction-game.py** script in the root directory of the project.

Alternatively, you can run both use cases by directly running their main scripts in their respective directories ([main](./editable-plots/main.py) for chart editor and [main](./prediction-game/main.py) for prediction game).

Make sure that your Python interpreter has installed all external dependencies.
These are:

**kiwisolver**

Install using pip:
```bash
pip install kiwisolver
```
Required minimal version is 1.5.0.

**Pillow**

Install using pip:
```bash
pip install pillow
```
Required minimal version is 12.1.1.

## Prediction game examples
Prediction game examples can be found in directory [game examples](./game%20examples/).

## Developer documentation
To generate documentation for this project, you will need sphinx library.
The build needs all external dependencies to be installed.

Install it using
```bash
pip install sphinx
```
Then in the [docs](./docs/) directory run makefile to build HTML of the documentation.

On linux run:
```bash
make html
```

On windows run:
```bash
.\make.bat html
```

The resulting documentation should be created in the build directory in [docs](./docs/) directory.
