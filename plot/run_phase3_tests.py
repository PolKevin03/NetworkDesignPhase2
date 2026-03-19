import subprocess
import time
import csv

FILE = "../input/bmp_24.bmp"

rates = [0.0, 0.25, 0.5, 0.75, 0.9]
trials = 2   
results = []

def run_option4(rate):
    start = time.time()

    server = subprocess.Popen(
        ["python", "server_rdt22notupdated.py"],
        cwd="Option4"
    )

    time.sleep(0.5)

    subprocess.run(
        ["python", "client_rdt30.py", FILE, str(rate)],
        cwd="Option4"
    )

    server.terminate()
    server.wait()

    return time.time() - start


def run_option5(rate):
    start = time.time()

    server = subprocess.Popen(
        ["python", "server_rdt30updated.py", str(rate)],
        cwd="Option5"
    )

    time.sleep(0.5)

    subprocess.run(
        ["python", "client_rdt30notupdated.py", FILE],
        cwd="Option5"
    )

    server.terminate()
    server.wait()

    return time.time() - start


print("\nOption 4 (ACK loss)\n")

for r in rates:
    times = []
    print(f"rate {r}")

    for i in range(trials):
        t = run_option4(r)
        times.append(t)
        print(f"  trial {i+1}: {t:.3f}s")

    avg = sum(times) / len(times)
    print(f"  avg: {avg:.3f}s\n")

    results.append(["4", r, avg])


print("\nOption 5 (DATA loss)\n")

for r in rates:
    times = []
    print(f"rate {r}")

    for i in range(trials):
        t = run_option5(r)
        times.append(t)
        print(f"  trial {i+1}: {t:.3f}s")

    avg = sum(times) / len(times)
    print(f"  avg: {avg:.3f}s\n")

    results.append(["5", r, avg])


with open("phase3_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["option", "rate", "avg_time"])
    writer.writerows(results)

print("\nSaved to phase3_results.csv")
