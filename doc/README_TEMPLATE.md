# Network Design Project – Team KOA

<!-- Optional: add badges if you want -->
<!-- ![language](https://img.shields.io/badge/language-python-blue) -->

## Overview
This repository implements a UDP/TCP-based file transfer protocol across **6 phases**, progressively adding reliability 
mechanisms and performance evaluation.

## Team
| Name | Email | Primary responsibility |
|---|---|---|
| Kevin Pol | Kevin_Pol@student.uml.edu | Opt.1 RDT2.2 packet format, and sender/reciever logic |
| Odey Khello | Odey_Khello@student.uml.edu | Opt.2 ACK bit error injection for sender |
| Andrew Thach | Andrew_Thach@student.uml.edu | Opt.3 Data packet bit injection for receiver and the plot  |

## Demo Video (submission)
- **Private YouTube link:** *(submit via Blackboard)*  
- **Timestamped outline:** *(mm:ss → scenario)*

---

## Repository Structure (required)
Your repo must match this layout (minimum):

```
src/        # sender, receiver, protocol utilities
scripts/    # experiment runner, plotting utilities
docs/       # design documents and diagrams
results/    # CSV + plots generated from experiments
input       #input test file
README.md
```

Optional (recommended):
- `tests/`
- `data/`
- `requirements.txt` (Python)

---

## Requirements
- Language/runtime: (Python 3.x)
- OS tested: (macOS / Windows / Linux)
- Dependencies:
  - Python: `pip install -r requirements.txt`

---

## Standard CLI Interface (required)
Your program must support these standardized flags so the TA can run and grade consistently.

### Receiver (required flags)
- `--port <int>`: UDP port to bind
- `--out <path>`: output file path to write received bytes
- `--seed <int>`: RNG seed (default: 0)
- `--log-level <debug|info|warning|error>` (default: info)

### Sender (required flags)
- `--host <ip/hostname>`: receiver host
- `--port <int>`: receiver port
- `--file <path>`: input file to send
- `--seed <int>`: RNG seed (default: 0)
- `--log-level <debug|info|warning|error>` (default: info)

### Injection flags (if required by phase)
- `--data-error-rate <float 0..1>` (default: 0)
- `--ack-error-rate <float 0..1>` (default: 0)
- `--data-loss-rate <float 0..1>` (default: 0)
- `--ack-loss-rate <float 0..1>` (default: 0)

### Timing / windowing flags (if required by phase)
- `--timeout-ms <int>` (default: 40)
- `--window-size <int>` (default: 10)

**Notes**
- “Rates” are probabilities per packet/ACK.
- Timing experiments must disable verbose logging (use `--log-level warning` or `error`).

---

## Quick Start (Run Locally)
### Start Receiver
```bash
python src/receiver.py --port 9000 --out results/received.bin --seed 0
```

### Run Sender
```bash
python src/sender.py --host 127.0.0.1 --port 9000 --file data/sample.jpg --seed 0
```

---

## Required Demo Scenarios (Current Phase)
Provide the exact commands used to demonstrate each required scenario.

### Scenario 1: ___Option 1_______
Receiver:
cd src
python server_rdt22.py

Sender:
cd src
python client_rdt22.py ..\input\bmp_24.bmp

Expected behavior:
- File will transfer with no errors and a recieved.bmp will come to file and match the input file

### Scenario 2: __Option 2________
Receiver:
cd src
python server_rdt22.py

Sender:
cd src
python client_rdt22_option2.py ..\input\bmp_24.bmp

Expected behavior:
- Sender will corrupt some ack packets and find some wrong checksum and complete the transfer which will match the original file
### Scenario 3: __Option 3________
Receiver:
cd src
python server_rdt22_option3.py

Sender:
cd src
python client_rdt22.py ..\input\bmp_24.bmp

Expected behavior:
- Reciever will corrupt some packets on data and the resend to ack and complete the transfer that matches the original

## Figures / Plots (if required by phase)
### Reproduce experiment runs
Your repo must include a script that can reproduce required sweeps and output CSV.

Example:
```bash
python scripts/run_experiments.py --phase 4 --out results/phase4.csv
```

### Generate plots
Example:
```bash
python scripts/plot_results.py --in results/phase4.csv --out results/phase4.png
```

### Results files
- `results/phaseX.csv`
- `results/phaseX.png`
- 'recieved.bmp'
---

## Known Issues / Limitations
List any limitations honestly.
- Stop and wait are only use
- port number were mixed up becuase teammates used different which held us back a bit
- spacing was always an issue for us
- this works with 1 client at a time
- another issue was the data record time/completion wasn't recorded weirdly for some reason, we couldn't get it to work
---

## Academic Integrity / External Tools
Debugging tools (IDE debugger, logging) and LLMs may be used for learning and troubleshooting. Final implementation decisions and understanding are our own.
