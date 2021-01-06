import schedule
import time
import subprocess

def remind():
    subprocess.run(["teachable_remind"])
    return

def main():
    schedule.every().saturday.at("13:15").do(remind)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
