Synthetica is a stylised open-world 3D sandbox with a number of biome regions and pseudo-intelligent fractal-esque creatures that inhabit the area. The player can interact with these creatures and resources, relocate them, and in general experience the moving world. It stores all the world’s data in a giant list of dictionaries, which are indexed and updated according to the player’s position in the world and interactions that happen within the world while the player is looking As a general play strategy - it’s probably most fun to collect/distribute resources and try to get the creatures to reach higher and higher levels of recursion! At a certain point many of them will cease recursing further and instead exhibit animated behaviours. 


This code requires Processing Python Mode to run and render, as it contains many of Processing’s built in draw functions. However, simply viewing the code in plaintext can be done by opening up the main .pyde and subsidiary .py functions in any plaintext editor.

Note: while the default settings are recommended for play, the world does still take a short while to generate on larger settings and the game may appear to not be working - this is not the case :) Thanks for your patience. ‘Synthetic’ setting refers to the maximum possible setting for any parameter. Setting “sight” to synthetic may result in quite slow FPS, but all other parameters can be set to taste. 


Mac and Windows applications have been packaged for convenience. Latest install of java 7 is required. 

TO RUN THIS CODE:

1.
Download Processing here:
https://processing.org

2.
Follow the instructions to install Python mode here:
https://github.com/jdf/processing.py#python-mode-for-processing

3.
In the folder Synthetica, run the file Synthetica.pyde. This will open the python code (and all its tabs) in the Processing IDE. To run, simply do CMD+R or press the “Play” button at the top of the IDE window. Press ESC to close.