import serial.tools.list_ports

from . import Mss, Adalight
from pathlib import Path
from json import dump, load
import click


def load_config() -> dict:
    config_path = Path.home() / "pyadalight.json"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return load(f)


def save_config(config: dict) -> None:
    config_path = Path.home() / "pyadalight.json"
    with open(config_path, "w") as f:
        return dump(config, f)


def validate_config(config: dict) -> None:
    assert "h_led_count" in config, "Horizontal LED count is not set."
    assert "v_led_count" in config, "Vertical LED count is not set."
    assert "port" in config, "Serial port set."
    assert "monitor" in config, "Monitor index is not set."

    h_led_count = config["h_led_count"]
    v_led_count = config["v_led_count"]
    port = config["port"]
    monitor = config["monitor"]

    assert isinstance(h_led_count, int), f"h_led_count must be int, not {type(h_led_count)}"
    assert isinstance(v_led_count, int), f"v_led_count must be int, not {type(v_led_count)}"
    assert isinstance(port, str), f"h_led_count must be str, not {type(port)}"
    assert isinstance(monitor, int), f"h_led_count must be int, not {type(monitor)}"

    assert h_led_count > 0, "h_led_count must be greater than 0."
    assert v_led_count > 0, "v_led_count must be greater than 0."

    assert 0 < monitor < len(Mss().monitors), f"monitor must be greater than 0 and lower than " \
                                              f"{len(Mss().monitors)}."


@click.command()
@click.option("--h-led-count", "-hl", "h_led_count", type=int, help="Horizontal LED count.")
@click.option("--v-led-count", "-vl", "v_led_count", type=int, help="Vertical LED count.")
@click.option("--port", "-p", "port", type=str, help="Serial port.")
@click.option("--monitor", "-m", "monitor", type=int, help="Monitor index.")
@click.option("--list-monitors", "list_monitors", is_flag=True, default=False, help="Shows monitors list and exits.")
@click.option("--list-ports", "list_ports", is_flag=True, default=False, help="Shows ports list and exits.")
def main(h_led_count: int = None, v_led_count: int = None, port: str = None, monitor: int = None,
         list_monitors: bool = None,
         list_ports: bool = None):
    if list_monitors:
        print("Monitors: ")
        for idx, mon in enumerate(Mss().monitors):
            print(f"\t{idx}\t{mon}")
        if not list_ports: return

    if list_ports:
        print("Ports: ")
        for port, desc, hwid in serial.tools.list_ports.comports():
            print(f"\t{port}\t{desc} [{hwid}]")
        return

    conf = load_config()
    if h_led_count is not None:
        conf["h_led_count"] = h_led_count
    if v_led_count is not None:
        conf["v_led_count"] = v_led_count
    if port is not None:
        conf["port"] = port
    if monitor is not None:
        conf["monitor"] = monitor

    try:
        validate_config(conf)
    except AssertionError as e:
        print(f"Error: {e}")
        return

    save_config(conf)

    mon = Mss().monitors[conf["monitor"]]
    ada = Adalight(conf["h_led_count"], conf["v_led_count"], conf["port"], mon)
    print("Running pyAdalight, press Ctrl+C to stop.")
    ada.run()


if __name__ == "__main__":
    main()
