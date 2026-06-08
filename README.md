# MinGenResources-DFW
Using persistent homology and minimal generators for resource allocation. Project for: 2026 Data Science REU@SMU


| Folder Name | Contents |
| ----------- | --------- |
| Data | Link to data files needed for this project. (the actual files are stored on Box because they are too big) |
| Distance Matrix | Code to compurte pairwise distances between sets of points |
| Minimal Scaffold | Code to read in a matrix of distances, compute a VR filtration, and track cycles through time. |
| src | Source code for MinScaffold (see citation below) 


### This project makes significant use of:

## MinScaffold
Python3 implementation of the Minimal Homological Scaffold 
(Dey, Li, Wang: Efficient algorithms for computing a minimal homology basis. Latin American Symposium on Theoretical Informatics (2018))
Marco Guerra, Alessandro De Gregorio (2019)

We have extracted only the core functionality we needed for the project

For the full package, see: https://github.com/marcoguerra192/MinScaffold

