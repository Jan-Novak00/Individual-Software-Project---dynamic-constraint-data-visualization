# Software specification & implementation schedule for Dynamic data visualisation using constraint solving

This project focuses on developing a dynamic data visualization and manipulation tool using the Cassowary constraint solver. The objective is to create an intuitive and interactive tool that allows the user to modify data directly from the visualized plots.

Version: #ToDo

Author: Jan Novák

Date: #ToDo 

## Table of Contents
#ToDo 

## 1. Project Overview

### 1.1 Decription and Scope of the Software

This project aims to develop a dynamic data visualization tool using the Cassowary constraint solver to create interactive plots. Manipulation of the plots is designed to be intuitive, allowing users to adjust parameters such as scale or bar height in bar charts through direct interaction with plot elements. Users can modify the underlying data in real time simply by interacting with the plot components.

The inspiration for this tool comes from the Fluid programming language. Our implementation focuses on usability and intuitiveness, targeting users without technical backgrounds.
### 1.2 Used Technologies
- Python
- kiwisolver (implementation of the Cassowary constraint solver)
- #ToDo (visualisation libraries)

### 1.3 External references
#ToDo 
- kiwisolver documentation
	- [https://kiwisolver.readthedocs.io/en/latest/](https://kiwisolver.readthedocs.io/en/latest/), The Nucleic Development Team, 2024

### 1.4 Documentation Conventions
#ToDo 
#Optional 

## 2. Software Summary
### 2.1 Reason for the Software Development and Its Main Components and Objectives
#ToDo
### 2.2 Main functions

- creation of several types of plots from input data
	- such as bar chart, boxplot or candlestick chart
- direct plot manipulation
	- such as bar height, axis scale
- direct data manipulation via created plot
### 2.3 Motivational Use Case

- the user inputs the data as an array of numbers into the system.
- the user selects "bar chart" option and specifies axis units and plot title
- the system generates the plot
- the user adjusts the spacing between bars by interacting directly with the plot elements (e.g., clicking and dragging).“
- the user selects a specific bar and modifies its height using the cursor.“
	- the system adjusts the data to fit the new bar height
- the user stores the final plot and modified data

### 2.4 Aplication environment
#ToDo 

### 2.5 Project Limitations
#ToDo 
The main limitation is the constraint solver technology which enables us to only create "rectangle based plot", i.e. plots where the data is visualized by rectangles.

## 3. External interface
#ToDo 

## Detailed Functional Description
#ToDo 

## Screens
#ToDo 
#Optional

## Non-Functional Requirements
#ToDo 
#Optional 

## Time-line & Milestones
#ToDo 

## Notes
#ToDo 
#Optional
