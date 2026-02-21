# Option 2 (ACK packet bit-error at sender) - RDT 2.2 over UDP

This bundle follows the same structure as the Option 1 code (`client_rdt22.py`, `server_rdt22.py`, `rdt_utils.py`).

## What changed for Option 2
Only the **sender** (`client_rdt22.py`) was modified to intentionally corrupt received ACK packets **after** `recvfrom()` at the sender side.

- If ACK is corrupted or wrong sequence number -> sender resends the same DATA packet (RDT 2.2 behavior).
- Receiver code is unchanged.

## Files in this zip
- `client_rdt22.py` -> Option 2 sender (ACK bit-error injection at sender)
- `server_rdt22.py` -> receiver (same structure)
- `rdt_utils.py` -> packet format + checksum
- `bmp_24.bmp` -> sample input file for quick demo

## Run 
### Terminal 1 (receiver)
```bash
python server_rdt22.py
```

### Terminal 2 (sender)
No error injection (acts like Option 1 behavior):
```bash
python client_rdt22.py bmp_24.bmp 0.0 42
```

Option 2 demo (ACK bit-error injection at sender):
```bash
python client_rdt22.py bmp_24.bmp 0.30 42
```

Arguments:
- `file.bmp` = input file
- `ack_error_rate` = probability from `0` to `1` to corrupt a received ACK at sender
- `seed` = random seed for repeatable demo (optional)

## Verify output matches input (optional)
After transfer, compare files:
```bash
cmp bmp_24.bmp received.bmp
```
If no output from `cmp`, files match.

## Notes for your team merge
- Keep `rdt_utils.py` packet format the same across all options.
- Option 2 should only change the sender ACK receive path injection logic.
