import os

import pandas as pd
import plotly.express as px
import json
import plotly
import plotly.colors as pc


import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_dfs():

    runs = []
    for file in ["logs/distributed_nn_12_strategy_pub_sub/"+f for f in os.listdir("logs/distributed_nn_12_strategy_pub_sub/") if f.startswith('run-app-init')]:
        with open(file,'r') as f:
            runs += json.load(f)
    app_init_df = pd.DataFrame(runs)
    app_init_df = app_init_df.astype({'setup_time_ms': 'int32', 'missing_acks': 'int32'})

    for file in ["logs/distributed_nn_12_strategy_pub_sub/"+f for f in os.listdir("logs/distributed_nn_12_strategy_pub_sub/") if f.startswith('run-app-inference')]:
        with open(file,'r') as f:
            runs += json.load(f)
    app_inference_df = pd.DataFrame(runs)
    app_inference_df = app_inference_df.astype({'setup_time_ms': 'int32', 'missing_acks': 'int32'})

    runs = []
    with open('logs/distributed_nn_12_strategy_pub_sub/run-continuous-messages-0.json', 'r') as f:
        runs += json.load(f)
    message_continuous_df = pd.DataFrame(runs)
    message_continuous_df = message_continuous_df.astype(
        {'timestamp': 'float64', 'messageType': 'str', 'strategyType': 'str', 'messageSubtype': 'str',
         'n_bytes': 'int32'})

    return app_init_df,app_inference_df,message_continuous_df



if __name__ == '__main__':
    app_init_df,app_inference_df,message_continuous_df = get_dfs()

    with pd.option_context('display.max_rows', None,'display.max_columns', None,'display.width', None,'display.max_colwidth', None):
         print(app_init_df)
         print(app_inference_df)
         print(message_continuous_df)



