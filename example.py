from pyadalight import Mss, Adalight


def main():
    h_led_count = int(input("Horizontal LED count: "))
    v_led_count = int(input("Vertical LED count: "))

    print("Choose monitor: ")
    for idx, mon in enumerate(Mss().monitors):
        print(f"\t{idx}\t{mon}")
    mon = Mss().monitors[int(input("-> "))]
    ada = Adalight(h_led_count, v_led_count, "/dev/ttyUSB0", mon)
    ada.run_in_thread()
    while True:
        inp = input()
        if inp == "stop":
            ada.stop()
        elif inp == "start":
            ada.run_in_thread()
        elif inp == "exit":
            break


if __name__ == "__main__":
    main()
