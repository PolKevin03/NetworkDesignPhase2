# Network Design Project – Phase Proposal & Design Document (Phase _2_ of 5)

> **Purpose:** This document is your team’s *proposal* for how you will implement the current phase **before** you start coding.  
> Keep it clear, concrete, and lightweight.

**Team Name:**  
**Members:** (Kevin Pol, Kevin_Pol@student.uml.edu)  
**GitHub Repo URL (with GitHub usernames):** PolKevin03  
**Phase:** (2)  
**Submission Date:*2/13/2026*  
**Version:** (v1)

---

## 0) Executive summary

  In Phase 2, I will implement the RDT 2.2 reliable data transfer protocol over the UDP channel using bit errors. This builds on Phase 1 by being reliabile and having features like a sequence numbers, checksums, and acknowledgment packets. The protocol uses a stop-and-wait method with alternating sequence numbers of zeros and ones. A BMP file will be split into packets, sent by the sender, and checked and put back together by the receiver. I will test three cases which are no errors, crashed acknowledgment packets, and crashed data packets. If errors occur, packets will be resent until they are received correctly. The transfer is complete when the output file is the same as the input file.

---

## 1) Phase requirements
### 1.1 Demo deliverable N/A
You will submit a **screen recording** demonstrating the required scenarios.

- **Private YouTube link:** N/A  *(fill in at submission time)*  
  - Link:
  - Timestamped outline (mm:ss → scenario name):

### 1.2 Required demo scenarios
Fill in the scenarios required by the phase spec.

| Scenario | What you will inject / configure | Expected observable behavior | What we will see in the video |
|---|---|---|---|
| 1 | No bit errors | Normal stop and wait transfer | File transfer clean and matches |
| 2 | Corrupt ACK packet at sender | Sender sees ACK | Packets sent again and transfers done |
| 3 | Corrupt data packet at reciever | Finds bad data | Packet resent until file transfer right |

### 1.3 Required figures / plots N/A
Fill in the figures/plots required by the phase spec (if none, write “N/A”).

| Figure/Plot | X-axis | Y-axis | Sweep range + step | Data source (CSV/log) | Output filename |
|---|---|---|---|---|---|
| 1 | Time vs Error Rate | Error | Time | 0-95 step 5 | plot1.png |
| 2 | Time vs Error Rate | Error | Time | 0-95 step 5 | plot2.png |

---

## 2) Phase plan (company-style, lightweight)
Think of this as a short “implementation proposal” you’d write at a company.

### 2.1 Scope: what changes/additions this phase
- **New behaviors added:**
- **Behaviors unchanged from previous phase:**
- **Out of scope (explicitly):**
- Implement RDT 2.2 stop-and-wait sender and receiver logic numbers 0 and 1.
- Add a packet header with type, sequence number, length, and checksum.
- Add checksum checking to find corrupted packets.
- Add acknowledgment handling middle of sender and receiver.
- Add bit-error for below
- Corrupted acknowledgment packets 
- Corrupted data packets 
- Add an experiment mode to measure completion time from 0% to 95% error rate.

### 2.2 Acceptance criteria (your checklist)
List 5–10 measurable checks that mean you’re done (examples below).

- [ ] Sender and receiver run correctly.
- [ ] All three scenarios are demonstrated.
- [ ] File transfers successfully with no corruption.
- [ ] Corrupted packets are detected and handled
- [ ] Output file matches the input file.
- [ ] Completion-time data and plots are generated.

### 2.3 Work breakdown (high-level; Person X will work on A, Person Y will work on B...)
- Workstream A: Packet format and checksum making
- Workstream B: RDT 2.2 sender logic and ack making
- Workstream C: RDT 2.2 reciever logic, and error checking

---

## 3) Architecture + state diagrams
Your phase specs likely include a reference state diagram. **You should build on it across phases.**

### 3.1 How to evolve the provided state diagram
I will use the sender and receiver state diagrams provided for RDT 2.2. These show the stop-and-wait process using sequence numbers 0 and 1. The sender resends packets if acknowledgments are wrong or corrupted, and the receiver resends the last acknowledgment if data is corrupted or unexpected. The provided diagrams will be in the submission.

1. **Start from the current phase diagram** N/A(sender + receiver).
2. **Mark specifics**:
   - new states,
   - new transitions,
   - updated transition conditions (timeouts, corruption checks, window slide rules).
3. Keep both:
   - **“Previous phase diagram”** (for comparison) and
   - **“Current phase diagram”** (what you will implement in more detail).

> Tip: In your PDF submission, include diagrams as images. In Markdown, you can include ASCII diagrams or link to images in `docs/figures/`.

### 3.2 Component responsibilities
- **Sender**
  - responsibilities:
Split file into packets.
Add sequence numbers and checksums.
Send packets and wait for acknowledgments.
- **Receiver**
  - responsibilities:
Check packets for errors.
Accept correct packets in order.
Send acknowledgments and write the file.
- **Shared modules/utilities**
  - packet encode/decode:
  - checksum: checking
  - logging/timing:
  - CLI/config parsing:

### 3.3 Message flow overview
Add a simple diagram (box + arrows is fine, you're also welcome to use software with screenshots).

Example:
```
[file] -> Sender -> UDP -> Receiver -> [output file]
              ^             |
              |---- ACK ----|
```

---

## 4) Packet format (high-level spec)
Define your on-the-wire format **unambiguously**.

### 4.1 Packet types
List the packet types you will send:
- Data packet
- ACK packet
- (Optional) end-of-transfer marker / metadata packet

### 4.2 Header fields (this is the “field table”)
**What this means:** you must specify the *exact* fields in each packet header and their meaning.  
This ensures everyone can encode/decode packets consistently.

| Field | Size (bytes/bits) | Type | Description | Notes |
|---|---:|---|---|---|
| type | 1 byte | int | data or ack | find packet type |
| seq | 1 byte| int | sequence number | 0 or 1 |
| ack | 1 byte| int | ack number | use ack packets |
| len | 2 byte| int | payload length | last packet may be smaller |
| checksum | 4 byte| int | checksum/error value | covers (header/payload) |
| payload | ≤ ~1024B | bytes | file data | binary-safe |

---

## 5) Data structures + module map
This section prevents “random globals everywhere” and helps keep code maintainable.

### 5.1 Key data structures
List the core structures you will store in memory.

Sender:
Sequence number (0 or 1)
Last packet sent 
File chunks to send
Receiver:
Expected sequence number
Last acknowledgment sent
Output file buffer
Metrics (for plots):
Error rate
Completion time
Attempt number

### 5.2 Module map + dependencies
Show how modules connect.

Minimum expected modules (names may vary):
- `src/sender.*`
- `src/receiver.*`
- `src/packet.*` (encode/decode)
- `src/checksum.*`
- `scripts/run_experiments.*` (if applicable)
- `scripts/plot_results.*` (if applicable)

Provide a simple dependency sketch: 

```
sender -> packet, checksum, utils
receiver -> packet, checksum, utils
scripts -> sender/receiver CLI, results CSV, plotting
```

---

## 6) Protocol logic (high-level spec before implementation)
This section is your “engineering spec” that you implement against. Keep it precise but not code-heavy.

### 6.1 Sender behavior
Describe behavior as steps or a state machine:
- Split file into packets.
- Send one packet and wait for ACK.
- If ACK is bad or wrong, send again.
- If correct, move to next packet and different sequence number.

**Sender pseudocode (recommended):** N/A
```text
initialize state
while not done:
  send/queue packets according to phase rules
  wait for ACK/event
  if ACK received:
    validate (checksum/seq)
    update state (advance, ignore duplicate, etc.)
  if timeout/event:
    retransmit according to phase rules
```

### 6.2 Receiver behavior
Describe receiver rules:
-Receive packet and check for errors.
- If correct and expected, write data and send ACK.
- If corrupted or unexpected, resend last ACK.

**Receiver pseudocode (recommended):**
```text
on packet receive:
  if corrupt: discard; respond according to phase rules
  else if expected: accept; write/buffer; ACK
  else: handle duplicate/out-of-order according to phase rules
```

### 6.3 Error/loss injection spec (if required by phase)
If the phase requires injection, state:
- where injection occurs in the pipeline (exact point)
- Corrupt ACKs at sender.
- Corrupt DATA at receiver.
- Bit errors based on error rate.
- Random seed for repeatable tests.

---

## 7) Experiments + metrics plan (required if phase requires figures/plots)
### 7.1 Measurement definition
Define completion time precisely:
- start moment:when first packet is sent
- stop moment:when transfer finishes

State how you will avoid measurement distortion:
- disable verbose printing/logging during timing runs
- run multiple trials if required

### 7.2 Output artifacts
- CSV schema (columns): error rate and completion time
- plot filenames: in results/
- where outputs are stored (`results/`):

---

## 8) Edge cases + test plan
This replaces “risks” with what actually matters for correctness.

### 8.1 Edge cases you expect
List the top edge cases you will explicitly test.

| Edge case | Why it matters | Expected behavior |
|---|---|---|
| last packet smaller than normal size | correct file reconstruction | receiver writes exact bytes |
| duplicate packets/ACKs | during resend | ignored or re-ACKed |
| corrupted header | error check | packet drop |
| termination marker handling | clean shutdown | no deadlocks |

### 8.2 Tests you will write because of these edge cases
List concrete tests (unit/integration) that map to the edge cases.

- Send file and confirm output matches input.
- Find errors and confirm transfer still completes.
- Verify checksum detects corruption.

### 8.3 Test artifacts
State what artifacts you will produce:
- console logs (minimal)
- where tests live (`tests/` optional, or `scripts/`)

---

## 9) Repo structure + reproducibility
Your repo must contain at minimum:

```
src/
scripts/
docs/
results/
README.md
```

State where phase artifacts live:
- Design docs: `docs/`
- Figures/plots + CSV: `results/`
- Any helper scripts: `scripts/`

---

## 10) Team plan, ownership, and milestones
### 10.1 Task ownership
| Task | Owner | Target date | Definition of done |
|---|---|---|---|
| Packet format + encode/decode | Kevin Pol | 2/20 | packet built |
| Sender logic | Kevin Pol | 2/20 | sender has RDT rules |
| Receiver logic | Kevin Pol | 2/20 | Receiver write output |
| Option 2/ ACK biterror | Odey Khello | 2/20 | ACK corruption at sender causes resend + recovery |
| Option 3/Injection (if required) | Andrew Thach | 2/20 | ack corruption work |
| Figures/plots (if required) | Andrew Thach | 2/20 | save in result the plots |
| README + reproducibility | All | 2/20 | instructions |

### 10.2 Milestones (keep it realistic)
- Milestone 1:Packet format and checksum planned.
- Milestone 2:Sender and receiver basic transfer works.
- Milestone 3:Corruption scenarios work and plots are generated.

---

## Appendix (optional)
