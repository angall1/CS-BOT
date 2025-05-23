import asyncio
import sys
import signal

async def run_script(path):
    print(f"Starting {path}...")

    process = await asyncio.create_subprocess_exec(
        sys.executable, "-u", path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def read_stream(stream, name):
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"[{path} {name}] {line.decode(errors='replace').rstrip()}")

    await asyncio.gather(
        read_stream(process.stdout, "stdout"),
        read_stream(process.stderr, "stderr"),
    )

    await process.wait()
    print(f"{path} exited with code {process.returncode}")

async def main():
    tasks = [
        run_script("log_reader.py"),
        run_script("zeuscounter.py"),
        run_script("CS-Casino.py")
    ]
    await asyncio.gather(*tasks)

def shutdown():
    for task in asyncio.all_tasks():
        task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down cleanly...")
        shutdown()
