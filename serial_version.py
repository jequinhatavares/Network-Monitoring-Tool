import time
from unittest import skipIf

import serial
import threading

COM = 'COM4'
arduino = serial.Serial(port=COM, baudrate=115200, timeout=.1)

def read_serial():

   #arduino.write(bytes(x, 'utf-8'))
   print(f"Listening for serial on {COM}...")
   while True:
      #time.sleep(0.05)
      data = arduino.readline()
      if data != b'':
         try:
            message = data.decode()

            print(f"{message}")
            try:
               logging_module, *_ = message.split()

               if logging_module == '[D]':

                  logging_module, message_type, viz_message_type = message.split()

                  if viz_message_type == "0": #New node message
                     message_type, viz_message_type, node_IP, parent_IP = message.split()
                     print("DEBUG MESSAGE")

            except ValueError:
               print(f"Invalid message received: {message}")

         except ValueError:
            pass


               #if viz_message_type == '0':  # new node message

                  #G = load_graph()
                  #G.add_node(node_IP)
                  #if parent_IP != "None":
                  #   G.add_edge(parent_IP, node_IP)
                  #save_graph(G)

               # print("Nodes in G on UDP:", G.nodes())
               # print("Edges in G on UDP:", G.edges())



threading.Thread(target=read_serial, args=(), daemon=True).start()


#while True:
   #num = input("Enter a number: ") # Taking input from user
if __name__ == "__main__":
    while True:
       continue