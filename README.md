# Network Monitoring Tool

The network monitoring tool operates alongside HERMES and provides a real-time view of network topology formation.
In addition, the program monitors key network metrics, offering insight into system performance, communication patterns, and overall network behavior. 
This facilitates debugging, analysis, and a deeper understanding of the distributed system in operation.

<img width="1152" height="648" alt="NMT" src="https://github.com/user-attachments/assets/64ae2d67-d930-4f0f-b725-3dbaaff3acf3" />


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

Ensure that monitoring is enabled on the microcontrollers running HERMES. 
This can be done by activating the monitoring logs in the code:

```cpp
enableModule(MONITORING_SERVER);
```

Once the program is running, it will automatically start monitoring the network and displaying the topology in real time.
After initialization, a command-line interface (CLI) will appear with the available actions. Users can interact with the system as follows:

- Press `1` to display the metrics collected up to that moment.
- Press `2` to generate a JSON file containing the collected metrics.
- Press `8` to instruct the root node to send messages to each node in the network, enabling the measurement of Round Trip Time (RTT).

<p align="center">
  <img src="images/CLI.jpeg" width="600"/>
</p>