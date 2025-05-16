# RATA: An FE Heroes Simulator</h1>
### Version 2.7.3.1

RATA is a desktop application made with the Python language and Tkinter library which simulates and facilitates 
the gameplay of the Fire Emblem Heroes (2017) mobile game. Fire Emblem Heroes (FEH) is a strategy game developed
by Nintendo/Intelligent Systems featuring a cast of characters from the Fire Emblem series.

Users are given free access to the game's playable units and skills to experiment with. In the future, as the 
game's AI is further studied, more testing tools will be provided for more thorough testing of optimal layouts.
This project is also being made to preserve FEH's gameplay since it is a live service application with an eventual
sunset.

Runs on Python version 3.10. Tkinter widgets may not display or behave properly on Mac devices or may require resizing
the window to access all features.

Sprites and gameplay assets are downloaded from the https://feheroes.fandom.com page.

<h2>Current Features</h2>
<ul>
  <li>Access to all 1241 units playable (+Veronica, Bruno, Baldr, and Höðr).</li>
  <li>Play on the following maps: 50 Arena, 18 Aether Raids, all maps within Book I.</li>
  <li>Units can be freely customized with skills, levels, merges, supports, IVs, and more.</li>
  <li>Full map and combat simulations can be performed by complete user control, with the ability to undo actions.</li>
</ul>

<h2>Roadmap</h2>
<ul>
  <li>Add other types of modes (Grand Hero Battles, Summoner Duels, etc.).</li>
  <li>The ability to save maps and layouts.</li>
  <li>Ease of updating to obtain new units and downloading certain map files.</li>
  <li>More languages supported.</li>
  <li>Allow for enemy AI to control units.</li>
</ul>

<h2>How to Use</h2>

### Installation
1. Download the source code for a given version, or clone this repository.
   
```
$ git clone https://github.com/EtDet/RATA-Public
```


2. Install required packages by switching into the directory folder and installing requirements.
```
$ cd RATA-Public
```
```
$ pip install -r requirements.txt
```

3. Switch into the FEHSimulation folder and run sprites.py to download all unit sprites and map backgrounds.
```
$ cd FEHSimulation
```
```
$ python3 sprites.py
```

4. Run overview_menu.py to start the application.
```
$ python3 overview_menu.py
```

### Updating
1. Change into the FEHSimulation folder.
```
$ cd RATA-Public/FEHSimulation
```

2. Run updater.py to obtain the latest files.

```
$ python3 updater.py
```

3. If new sprites were added (New Heroes/Maps/Resplendents), sprites.py must be run to obtain them.
```
$ python3 sprites.py
```

<h2>Navigating RATA 2.0.0+</h2>
The new menu is broken into 5 sections: Map Selection, My Units, Main Display, Selected Unit Status, and Extras.

The Map Selection is a file directory-styled menu that stores maps to load. Folders can be expanded with a click, maps can be loaded by double-clicking it.

My Units will display a list of units currently saved to this device. You can search for units by name or build in the top search bar. "Create New" allows
you to build a new unit from scratch and can be saved once done. After selecting a unit in the list, you can choose to "Edit" or "Delete" them.

The Main Display will show the current map selected and handles gameplay. Up to 5 maps can be loaded at once and can be managed with the tabs on top. 
After loading a map from Map Selection, you can add your own units from the colored squares by either clicking them to add a new unit, or dragging a 
build from My Units. Right-click a placed unit to edit their build (this will only affect that unit on the map and will not affect any saved builds).
Double-click a placed unit to remove them from the map. Seasons can be selected from the bottom dropdowns. Once units are placed, you can start 
gameplay by clicking "Start Sim", and can be canceled by clicking "Stop Sim" Gameplay works similarly to FEH from here. "Undo Action" will undo the
last move.

The Selected Unit Status will display the current stats and skills of the currently selected unit from either My Units or the Main Display. Several
elements can be hovered over to display more info, such as skill descriptions or status effects.

The Extras panel contains 4 tabs will various info. The Player Units tab shows all player units currently active in which slots, and allows for bonus 
units to be set in model such as arena. The Enemy Units tab will perform similarly, without the option to set bonus units. The Forecasts tab will
enable once the simulation has started, and will display combat/assist/structure break forecasts when hovering. Building will allow for structures to
be placed in certain modes (to be added in the future).