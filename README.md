# Alive Cell Tracking Alpha
An Alpha version of tracking algorithm targeting alive cells with strong deformability, and without exposure of fluorescence.

---

This is an **[iGEM 2019](https://2019.igem.org)** product from team **[SUSTech_Shenzhen](https://2019.igem.org/Team:SUSTech_Shenzhen)**.

-   The design is discussed by *[Peter S](https://github.com/WingsUpete)* and *[Eric Huang](https://github.com/Eric-HYQ)*.

-   The coding is mainly completed by *Peter S*.

-   The GUI interface is implemented by *[Huang Chaoxin](https://github.com/teachmain)*.

---

For researchers and iGEMers, feel free to use this tool if you want to keep track of alive cells for a relatively large amount of time, and without using dye or fluorescence.

However, be aware that this is **only a prototype**, meaning that under certain occasions it may not work well as expected. More tests and adjustments are needed in the current stage.



## Features

-   Customizable Parameters
-   Simple GUI Interface with File Chooser
-   Visualized Cell Selectors
-   Real-time Tracking View
-   Precise Missing Detection and Multitracker Reinitialization
-   Scalable Output Dataset
-   Additional Data Analysis Script



## Getting Started





## Motivation

In our project, we need to keep track of HL60 to see whether its movement has been affected by IL8. Specifically, we hope to keep our cells alive for a certain amount of time and thus we cannot expose them under fluorescence all the time.
The other problem is that each tracking process produces more than 1500 frames, which makes it a nightmare for researchers who want to point out each cell manually.
If we can build a simple software to somehow track down as many cells per frame as we can, and control the precision under a specified level in the meantime, the problems above might be solved.



## Current Situation

For the time being, most of the cell trackers available online are only able to detect the positions of deal cells, rather than tracking moving cells.

There are also plenty specific to keeping track of molecules in the cellular environment, but the molecules are also processed with fluorescence, which does not meet our needs.
In general, we need an approach to keep track of cells that are:

-   Alive
-   Probably morphologic, and
-   Have not been processed by dye or fluorescence.



## Roadblocks

We are encountering lots of problems during implementations, listed as below:
1. The cells we are targeting are morphologic. The shape of the cells are not fixed.
2. Due to limited time, it seems not feasible to implement a tracker from scratch. For existing trackers however, there are chances that they fail on tracking cells.
3. With the OpenCV Multi-Tracker API, dynamic handling of cell coordinates as `Numpy` arrays are required. **Dynamic** specifies the difficulty.
4. With the existing tracker such as CSRT, learned filter sets for cells are not abundant. Before detection is fully functional, the tracking process can still get easily interrupted when certain cells are missing.



## Ideas and Design

-   There are 8 standard trackers in the OpenCV package:

`BOOSTING`, `MIL`, `KCF`, `TLD`, `MEDIANFLOW`, `GOTURN`, `MOSSE`, `CSRT`

After testing each tracker, we found that CSRT tracker has the best tracking precision on cells.

CSRT is also specified as CSR-DCF (*Discriminative Correlation Filter Tracker with Channel and Spatial Reliability*). It considers using learned filter sets to detect possible objects with channel and spatial reliability. With this tracker, we are able to locate each cell at a nice precision.

-   For a period of time, we tried to implement the platform under *C++*, but later on we switched to *Python*, because the plotting tool (`Matplotlib`) and the file chooser (`tkinter`) can be easily packed into the platform.

-   The next thing to consider seriously is the missing judgment.

    If a cell gets lost, there are two conditions:

    1.  The multi-tracker claims to lose track of it.
    2.  The cell may not be alive anymore, so it is “sitting” in the video. Or under slight turbulences, it seems to “dawdle” around. When this happens in more than a certain number of continuous frames, it may be necessary to doubt whether this cell is still alive or not.

---

Using the idea above, we drew a flow chart to further extend our ideas:

[graph](#)





## Implementation

The main algorithm follows the current pseudocode:

```python
Handle all parameters in the GUI platform
start the program by reading a source video
select cells to track
assign random colors to new selected cells
initialize a multi-tracker
keep track of the cells until the tracker finishes its life cycle, or the number of missing cells exceeds the threshold
If the user wants to continue adding new cells, jump to step 3 (the selection process). If the user wants to finish, go to the next step
save the data of tracking cells' positions into a file
use the data to plot out a graph
finish
```

To check the detailed implementations, visit the *Github* page of our project.

The timeline of our implementations is as follow:

1.  Implement basic multi-tracker function.
2.  Dig out the parameters and divide them into an individual file - `Config.py`.
3.  Add a file chooser to let the user choose the source video using a more visualized view.

4.  Implement the plotting function to plot the results.
5.  Handle the data saving process.
6.  Further implement the miss detection procedure to detect missing cells and delete them from the dataset.
7.  When cells are missing, their previous data may still be valuable. Check whether the maximum continuous valid frames these cells endure have exceeded the threshold.
8.  Implement a simple GUI to manage the parameters.



## A Simple Demo of our Platform





## License

The license we use for this project is **CC by 4.0**.

Please check the file: [CC4.0.license](CC4.0.license).



## About SUSTech_Shenzhen 2019: C-hoop

The name “C-hoop” is derived from “Constraint hoop”, an artifact used to restrict the power of Monkey King. Our “hoop” is used to manipulate the mammalian cell behavior.

For more details, check our **[Description](https://2019.igem.org/Team:SUSTech_Shenzhen/Description)** page.

