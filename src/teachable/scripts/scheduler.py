import schedule
import time
import subprocess


def remind():
    subprocess.run(["teachable_remind"])
    return


def statements():
    subprocess.run(["teachable_statements", "-e"])
    return


def main():
    schedule.every().saturday.at("13:15").do(remind)
    schedule.every().saturday.at("13:15").do(statements)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
