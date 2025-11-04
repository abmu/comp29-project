# SUMO Environment

## Usage
To generate new entity routes, change into the `scripts/` folder, adjust the `generate_routes.py` file as necessary, and then run it:
```
cd .\scripts\
python .\generate_routes.py
```

To run the simulation, go to the local root directory, and run the following:
```
sumo-gui .\simulation.sumocfg
```


## Network Guide
Lanes names:
- (Street Name)\_(Lane Number)\_(Segment Number)

Junction names: 
- EJ\_(X) -> End Junction X
- CJ\_(Y) -> Connecting Junction Y

Detector names:
- CJ\_(Y)\_(N/E/S/W)B_(Z) -> Connecting Junction Y, N/E/S/W Bound Lane Z


## Random Notes
Press 'F10' in netedit and ensure the 'lefthand' options is set to true
Press 'F9' in netedit, go to 'Junctions', and click 'Show link tls index'


## Dependencies
Before you begin, ensure you have Simulation of Urban MObility (SUMO) installed.