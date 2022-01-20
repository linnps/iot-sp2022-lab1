from time import sleep
import picar_4wd as fc

speed = 40


def main():
    while True:
        scan_list = fc.scan_step(37)
        if not scan_list:
            continue
        scan_focus = scan_list[3:7]

        if scan_focus != [2, 2, 2, 2]:
            fc.backward(speed)
            sleep(0.3)
            fc.turn_left(speed)
            sleep(0.2)
        else:
            fc.forward(speed)
            sleep(0.3)

    fc.stop()


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()