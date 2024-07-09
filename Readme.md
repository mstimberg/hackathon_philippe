# The Pause App

The repository hosts the source code for the "Pause" Python app built for Philippe Aubert during the TOM Hackathon on July 8th-9th 2024.

## Function

The Pause app allows the user to navigate in local files from the Communicator 5 Text Files storage using keyword search and sorting by date of last modification. The text files are displayed on a side window.

The Pause app also lets the user automatically add appropriate pause tags to make the output of the Tobii text-to-speech utility from Communicator 5 more fluid.

TODO ADD SCREENSHOT HERE GABRIEL
![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)

## Important notes and issues

All files paths are hardcoded for use on Philippe's computer.

The .exe is not signed, so you will get a security warning from Windows when opening the app on Windows.

On Communicator 5 on Philippe's tablet version, opening an external program from a Communicator Home Screen shortcut seems to automatically trigger TD Control, which is inconvenient to use for Philippe.

Modified files including the pause tags are saved locally.

## How to Edit to App and update it on Philippe's computer

When you push a commit to main, the Github CI/CD triggers the build of the executable files for all platforms. For Philippe's computer, use the "latest" .exe.

You can download this .exe on Philippe's computer and run it to get the app. Replace the previous version so that the Communicator 5 Home Screen shortcut points to the latest version of the .exe.