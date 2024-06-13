# pentest_scenario
Penetration test scenario for research  project

Usage: 

step 1: move to folder /docker-compose
step 2: docker compose up -d
step 3: move to folder /src
step 4: start program with 'sudo python3 main.py'

How it works:

- Asks user to load or create a new session
- if new session: uses a clean (empty) TOSCA template file
- when performing scan, it updates the TOSCA tamplate appending compute nodes and webapps found
- if TOSCA file has nodes in it, displays a range of modules available (currently nmap, wappalyzer, DetectWebApp)
- user can select a node and send it to one of the modules for further analysis. Currently tested: nmap scan adds hosts (pts_compute), then each of them can be send to DetectWebApp. If a webapp is found, a node of type pts_webapp is added and the app is launched on the default browser.

Todo
- ensure modules correctly add data to TOSCA files
- check that final TOSCA template adheres to the one found in TOSCA-definitions for the demo scenario
- add more modules

