#!/usr/bin/python3

import torch
import torch.nn as nn
import sys
import connect4

CNN_MODEL = True
g_model = None

# Define the neural network
class Connect4Net(nn.Module):
    def __init__(self):
        super(Connect4Net, self).__init__()
        self.fc1 = nn.Linear(84, 256) # Hidden Layer
        self.fc2 = nn.Linear(256, 128) # Hidden Layer
        self.fc3 = nn.Linear(128, 128) # Hidden Layer
        self.fc4 = nn.Linear(128, 64) # Hidden layer
        self.fc5 = nn.Linear(64, 32)  # Hidden layer
        self.fc6 = nn.Linear(32, 7)   # Output layer

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.relu(self.fc5(x))
        x = self.fc6(x)  # No activation for output layer (logits)
        return x
    

class Connect4CNN(nn.Module):
    def __init__(self):
        super(Connect4CNN, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(2, 32, kernel_size=3, padding=1)  # Input: 2x6x7, Output: 32x6x7
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)  # Output: 64x6x7
        
        # Fully connected layers
        self.fc1 = nn.Linear(64 * 6 * 7, 128)  # Flattened output of conv2
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 7)  # Output layer (7 possible columns)

    def forward(self, x):
        x = torch.relu(self.conv1(x))  # Apply first conv + ReLU
        x = torch.relu(self.conv2(x))  # Apply second conv + ReLU
        x = x.view(x.size(0), -1)  # Flatten the feature map
        x = torch.relu(self.fc1(x))  # Fully connected layer 1
        x = torch.relu(self.fc2(x))  # Fully connected layer 2
        x = self.fc3(x)  # Output layer
        return x


def get_dl_best_move(board_state):
    # Convert the board state to a torch tensor
    board_tensor = torch.tensor(board_state, dtype=torch.float32).unsqueeze(0)  # Add batch dimension (1x84)

    # Run inference
    with torch.no_grad():
        output = g_model(board_tensor)  # Output is logits
        probabilities = torch.softmax(output, dim=1)  # Convert logits to probabilities
        predicted_column = torch.argmax(probabilities, dim=1).item()  # Get the column index

    return predicted_column


def get_cnn_best_move(board_state):
    # Convert to a tensor and reshape for the CNN
    input_tensor = torch.tensor(board_state, dtype=torch.float32).view(1, 2, 6, 7)

    # Perform inference
    with torch.no_grad():
        outputs = g_model(input_tensor)
        predicted_column = torch.argmax(outputs, dim=1).item()
    
    return predicted_column


def get_best_move(board_state):
    if CNN_MODEL:
        return get_cnn_best_move(board_state)
    else:
        return get_dl_best_move(board_state)


def get_board_state_vector(board):
    vec = []
    for r in range(board.rows):
        for c in range(board.columns):
            if board.board[r][c] == 1:
                vec.append(1)
                vec.append(0)
            elif board.board[r][c] == 2:
                vec.append(0)
                vec.append(1)
            else:
                vec.append(0)
                vec.append(0)

    return vec


def init_cnn_model():
    global g_model

    # Load the trained model
    g_model = Connect4CNN()
    g_model.load_state_dict(torch.load("model/connect4cnn.pth"))  # Load the saved weights
    g_model.eval()  # Set the model to evaluation mode

def init_dl_model():
    global g_model

    # Load the trained model
    g_model = Connect4Net()
    g_model.load_state_dict(torch.load("model/connect4dl.pth"))
    g_model.eval()

def init_model():
    if CNN_MODEL:
        init_cnn_model()
    else:
        init_dl_model()

init_model()

board = connect4.Board()
board.print_board()
while True:
    player = board.next_player
    if board.is_full():
        print("No more moves")
        sys.exit(0)

    while True:
        print(f"Player: {connect4.PLAYER_TEXT[player]}")
        userin = input("Enter column: ")
        try:
            col = int(userin.strip())
            if col < 0 or col > 6:
                print("Invalid column")
                continue
            break
        except ValueError:
            print("Invalid entry")
            continue
    ret = board.play(col)
    if ret != connect4.SUCCESS:
        print("Failed to make move")
        sys.exit(0)
    ret = board.check_win()
    board.print_board()
    if ret:
        print("User won!")
        sys.exit(0)

    if board.is_full():
        print("No more moves")
        sys.exit(0)

    print("Thinking...")
    eng = connect4.Connect4Engine(board)
    board_state_vector = get_board_state_vector(board)
    move = get_best_move(board_state_vector)
    ret = board.play(move)
    if ret != connect4.SUCCESS:
        print("Failed to make move")
        sys.exit(0)
    ret = board.check_win()
    board.print_board()
    if ret:
        print("Computer won!")
        sys.exit(0)
