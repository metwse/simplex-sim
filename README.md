# Computer Communications - Simplex Data Link Simulation
The first term project for the ITU Computer Communications Systems (BLG 337E)
course. This application provides a Tkinter interface for visualizing various
signal encoding/decoding/modulation/demodulation techniques.

## Installation
### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python3 -m src
```

## Supported Techniques
### Digital-to-Digital Encoding
NRZ-L, NRZ-I, Manchester, Differential Manchester, Bipolar AMI, Pseudoternary,
B8ZS, HDB3

### Analog-to-Digital Encoding
PCM, Delta Modulation

### Digital-to-Analog Modulation
ASK, FSK, PSK

### Analog-to-Analog Modulation
AM, FM, PM