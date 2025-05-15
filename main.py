import asyncio
import sys

async def run_script(path):
    process = await asyncio.create_subprocess_exec(
        sys.executable, path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if stdout:
        print(f"[{path}] stdout:\n{stdout.decode()}")
    if stderr:
        print(f"[{path}] stderr:\n{stderr.decode()}")

    return process.returncode

async def main():
    # Run both scripts concurrently
    await asyncio.gather(
        run_script("log_reader.py"),
        run_script("zeuscounter.py")
    )

if __name__ == "__main__":
    asyncio.run(main())
