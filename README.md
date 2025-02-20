# TLE Pass Predictor

## Overview
The TLE Pass Predictor is a Python project designed to fetch Two-Line Element (TLE) data for the CUAVA-2 satellite, predict its next pass over Sydney, and manage the execution of related commands. The project automates the process of tracking satellite passes and executing necessary commands at the predicted times.

## Project Structure
```
tle-pass-predictor
├── src
│   ├── main.py        # Main script for fetching TLE data and managing command execution
│   └── utils.py       # Utility functions for TLE fetching and time calculations
├── requirements.txt    # List of dependencies required for the project
└── README.md           # Documentation for the project
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd tle-pass-predictor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the main script, execute the following command:
```
python3 src/main.py -s CUAVA-2 &

Note that this can be repurposed to do WS-1 auto pass

```

## Functionality
- **Fetch TLE Data**: The script retrieves the latest TLE data for the CUAVA-2 satellite.
- **Predict Next Pass**: It calculates the next pass time over Sydney and converts it to local time.
- **Command Execution**: At the predicted pass time, the script executes specific commands and tracks their process IDs (PIDs).
- **Process Management**: The script terminates the processes after a specified duration post the predicted pass time.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.