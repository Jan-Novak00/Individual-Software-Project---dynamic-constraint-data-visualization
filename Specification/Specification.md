# **Software Specification & Implementation Schedule**

### *Dynamic Data Visualisation Using Constraint Solving*

---

**Anotation**  
This project focuses on developing a dynamic data visualization and manipulation tool using the Cassowary constraint solver. The objective is to create an intuitive and interactive tool that allows the user to modify data directly from the visualized plots.

---

**Version**: #ToDo  
**Author**: *Jan Novák*  
**Date**: #ToDo


## Table of Contents

- [1. Project Overview](#1-project-overview)
  - [1.1 Description and Scope of the Software](#11-decription-and-scope-of-the-software)
  - [1.2 Used Technologies](#12-used-technologies)
  - [1.3 External References](#13-external-references)
  - [1.4 Documentation Conventions](#14-documentation-conventions)
- [2. Software Summary](#2-software-summary)
  - [2.1 Reason for the Software Development and Its Main Components and Objectives](#21-reason-for-the-software-development-and-its-main-components-and-objectives)
  - [2.2 Main Functions](#22-main-functions)
  - [2.3 Motivational Use Case](#23-motivational-use-case)
  - [2.4 Aplication Environment](#24-aplication-environment)
  - [2.5 Project Limitations](#25-project-limitations)
- [3. External interface](#3-external-interface)
  - [3.1 User interface, inputs and outputs](#31-user-interface-inputs-and-outputs)
- [4. Detailed Functional Description](#4-detailed-functional-description)
  - [4.1 Plot Creation](#41-plot-creation)
  - [4.2 Plot Types](#42-plot-types)
  - [4.3 Plot Editing](#43-plot-editing)
  - [4.4 Data Manipulation](#44-data-manipulation)
- [5. Screens](#5-screens)
- [6. Non-Functional Requirements](#6-non-functional-requirements)
- [7. Time-line & Milestones](#7-time-line--milestones)




## 1. Project Overview

### 1.1 Description and Scope of the Software

This project aims to develop a dynamic data visualization tool using the Cassowary constraint solver to create interactive plots. Manipulation of the plots is designed to be intuitive, allowing users to adjust parameters such as scale or bar height in bar charts through direct interaction with plot elements. Users can modify the underlying data in real time simply by interacting with the plot components.

The inspiration for this tool comes from the Fluid programming language. Our implementation focuses on usability and intuitiveness, targeting users without technical backgrounds.

### 1.2 Used Technologies
- Python
- kiwisolver (implementation of the Cassowary constraint solver)
- #ToDo (visualisation libraries)

### 1.3 External References
- kiwisolver documentation
	- [https://kiwisolver.readthedocs.io/en/latest/](https://kiwisolver.readthedocs.io/en/latest/), The Nucleic Development Team, 2024

### 1.4 Documentation Conventions
- plot element - any visual element of generated plots 

## 2. Software Summary
### 2.1 Reason for the Software Development and Its Main Components and Objectives

The reason behind this project is to make plot creation and modification as intuitive and customizable as possible.

The other reason is to create an intuitive tool with which the user can modify data by manipulating generated plots. Existing tools with this feature are not suitable for non-technical users.

Main components:
- dialog window for plot creation and manipulation
- data view


### 2.2 Main Functions
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

### 2.4 Aplication Environment
The software will be debugged only for Windows 11, but no Windows-specific constructs will be used.

### 2.5 Project Limitations
The main limitation is the constraint solver technology which enables us to only create "rectangle based plots", i.e. plots where the data is visualized by rectangles.


## 3. External interface
### 3.1 User interface, inputs and outputs

The system will be implemented as a series of dialog windows for data input, plot generation, and plot/data manipulation.

The user inputs data either by directly copying them into a dialog window or by using an input file (e.g. in CSV or TXT format).

Through the dialog window, the user specifies the initial parameters of the plot — the title, axis units, column names, etc.  
After the plot is generated, the user can edit its components in another dialog window. If the user wishes to modify the input data, an additional dialog window will be displayed, showing in real time how the data are being manipulated.

The user can save both the plot and the data; the output will consist of a standard PNG image and a new file containing the edited data.


## 4. Detailed Functional Description
### 4.1 Plot Creation
The user inputs data they desire to visualize. Then they select the plot type they want to use, axis units, and using a text dialog or by clicking on the screen to define the plot dimensions, the graph is automatically generated using constraint solver.

### 4.2 Plot Types
Available plot types: (grouped) bar chart, histogram, boxplot, candlestick chart.

### 4.3 Plot Editing
The user can adjust plot elements by interacting with them (e.g. clicking and draging the side of bar in bar chart will adjust the width of all bars (or change any dimention of any type of plot elements), or by using a cursor they can adjust the spacing of plot elements, or rescale axes).

#### Edit example: bar chart
By clicking and dragging the right edge of any bar changes the width of all bars.


### 4.4 Data Manipulation
The user can switch to data manipulation mode where they can by manipulating certain plot elements (like bars or boxes) manipulate with input data. The user can see the change in data in real time.

## 5. Screens
#ToDo

## 6. Non-Functional Requirements
The system must provide an intuitive and accessible user interface that enables users to create and modify plots and data without the need for detailed instructions. 
Additionally, the system should allow for including the integration of new plot types.

## 7. Time-line & Milestones
#ToDo 

| Date      | Milestone                         | Method of Presentation             |
| --------- | --------------------------------- | ---------------------------------- |
| 18.5.2025 | Bar chart prototype in kiwisolver | Online meeting, code in repository |
| 17.6.2025 | Interactive barchart              | Online meeting, code in repository |
