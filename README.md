# connect4-ai
A CNN-based AI model to play connect-4 game

![Connect4 Screenshot](https://raw.githubusercontent.com/rachabathuni/connect4-ai/main/images/connect4.png)

# How to use
## Generate data
`gendata.py` generates a million positions and best move for each position as determined by the connect4 engine. Captures the data into `data/samples.csv`.

If you don't want to generte the data yourself, you can unzip the `samples.zip` file in the data directory.

## Run training
Use the `Connect4CNN.ipynb` Jupyter notebook to run training.  You can also use `connect4cnn.pth` pre-trained model if you don't want to train yourself.

## Play against AI
Use the `playai.py` script to play a game against AI. You can use `play.py` to use the connect4 engine to play against the engine for comparision

