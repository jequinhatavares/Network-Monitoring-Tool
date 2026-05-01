# Network Monitoring Tool

The network monitoring tool operates alongside HERMES and provides a real-time view of network topology formation.
In addition, the program monitors key network metrics, offering insight into system performance, communication patterns, and overall network behavior. 
This facilitates debugging, analysis, and a deeper understanding of the distributed system in operation.

## How Does It Work?

The tool operates by reading the serial output from the root node. 
The root node must be physically connected to the computer running the Network Monitoring Program, as it serves as the main data source for the system.

The HERMES library includes a dedicated logging mode designed specifically for this tool. This mode generates structured log messages containing all the information required for network monitoring and analysis. 
Within HERMES, a special message type was defined to clearly separate monitoring data from other communication.

The Network Monitoring Tool continuously reads the serial stream and filters messages of type `MONITORING`. 
These messages are then parsed according to a predefined format, extracting relevant fields such as node identifiers, timestamps, and network events.

After parsing, the data is stored in JSON files, organized sequentially by experiment. Each experiment dataset includes metrics such as network join events, parent recovery behavior, traffic distribution by message type, and distributed neural network activity.

## How to Run
The Network Monitoring Tool requires the root node of the network to be physically connected to the computer hosting the server.

First, install the required Python libraries:
```bash
pip install -r requirements.txt
```
Next, update the code to set the correct COM port where the root node is connected.

Once the program is running, it will automatically start monitoring the network and displaying the topology in real time.