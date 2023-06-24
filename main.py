from serial import Serial
from time import sleep, perf_counter
from mss import mss
import numpy as np
import cv2

MSS = mss()


def mkHeader(led_count: int) -> bytes:
    hi = (led_count << 8) & 0xff
    lo = led_count & 0xff

    check = int.to_bytes(hi ^ lo ^ 0x55, 1, "big")
    hi = int.to_bytes(hi, 1, "big")
    lo = int.to_bytes(lo, 1, "big")
    return b"Ada" + hi + lo + check


def main():
    with_corners = False
    h_led_count = int(input("Horizontal LED count: "))
    v_led_count = int(input("Vertical LED count: "))
    led_count = h_led_count * 2 + v_led_count * 2

    ser = Serial("/dev/ttyUSB0", 115200)
    assert ser.read(4) == b"Ada\n", "This is not adalight device"
    ser.write(mkHeader(led_count) + b"\xff\x00\x00" * led_count)
    sleep(.333)
    ser.write(mkHeader(led_count) + b"\x00\xff\x00" * led_count)
    sleep(.333)
    ser.write(mkHeader(led_count) + b"\x00\x00\xff" * led_count)
    sleep(.333)
    print("Choose monitor: ")
    for idx, mon in enumerate(MSS.monitors):
        print(f"\t{idx}\t{mon}")
    mon = MSS.monitors[int(input("-> "))]
    img = np.array(MSS.grab(mon))

    zones = [None] * led_count
    hw = (mon["width"]-100)//h_led_count
    hh = 100
    vw = 100
    vh = (mon["height"]-50)//v_led_count
    for i in range(led_count):  # Right to left direction
        ox = 0#mon["left"]
        oy = 0#mon["top"]
        if i in range(h_led_count):
            _i = i
            im = img[oy+mon["height"]-hh:oy+mon["height"], ox+mon["width"]-50-hw-hw*_i:ox+mon["width"]-50-hw*_i]  # 50 is corner offset
        elif i in range(h_led_count, h_led_count + v_led_count):
            _i = i - h_led_count
            im = img[oy+mon["height"]-25-vh-vh*_i:oy+mon["height"]-25-vh*_i, ox:ox+vw]  # 25 is corner offset
        elif i in range(h_led_count + v_led_count, h_led_count * 2 + v_led_count):
            _i = i - h_led_count - v_led_count
            im = img[oy:oy+hh, ox+50+hw*_i:ox+50+hw+hw*_i]  # 50 is corner offset
        elif i in range(h_led_count*2+v_led_count, h_led_count*2+v_led_count*2):
            _i = i - h_led_count*2 - v_led_count
            im = img[oy+25+vh*_i:oy+25+vh+vh*_i, ox+mon["width"]-vw:ox+mon["width"]]  # 25 is corner offset
        else:
            assert False, "This error must never happen"

        zones[i] = im  # TODO: calculate average color on each zone

    for idx, zone in enumerate(zones):
        cv2.imshow(f'Zone #{idx+1}', zone)
        cv2.waitKey(0)


if __name__ == "__main__":
    main()
