# RATA: An FE Heroes Simulator</h1>
### Version 1.0.7

RATA is a desktop application made with the Python language and Tkinter library which simulates and facilitates 
the gameplay of the Fire Emblem Heroes (2017) mobile game. Fire Emblem Heroes (FEH) is a strategy game developed
by Nintendo/Intelligent Systems featuring a cast of characters from the Fire Emblem series.

Users are given free access to the game's playable units and skills to experiment with. In the future, as the 
game's AI is further studied, more testing tools will be provided for more thorough testing of optimal layouts.
This project is also being made to preserve FEH's gameplay since it is a live service application with an eventual
sunset.

Runs on Python version 3.10.11. Tkinter widgets may not display properly on Mac devices and may require resizing
the window to access all features.

Sprites and gameplay assets are downloaded from the https://feheroes.fandom.com page.

<h2>Current Features</h2>
<ul>
  <li>Access to 316 units and the skills within their base kits.</li>
  <li>Units can be freely customized with skills, levels, merges, supports, and IVs.</li>
  <li>Full map and combat simulations can be performed on 20+ arena maps by complete user control.</li>
</ul>

<h2>Roadmap</h2>
<ul>
  <li>Add all units, skills, and mechanics.</li>
  <li>Add other types of modes (Aether Raids, Tempest Trials, Summoner Duels, etc.).</li>
  <li>Add enemy AI to test real situations in-game.</li>
</ul>

<h2>How to Use</h2>

1. Download the source code for a given version, or clone this repository.
   
```
$ git clone https://github.com/EtDet/RATA-Public
```


2. Install required packages.
```
$ cd RATA-Public
```
```
$ pip install -r requirements.txt
```

3. Run sprites.py to download all unit sprites and map backgrounds.
```
$ cd FEHSimulation
```
```
$ python3 sprites.py
```

4. Run menu.py to start the application.
```
$ python3 menu.py
```

If a new version of this repository is released, the sprites file must be rerun to repopulate files.

Personal unit data is stored within my_units.csv. This file can be copied into newer versions of this repository to continue using created units.
