KNOWN_UNITS_EXT = [
    ".automount",
    ".conf",
    ".link",
    ".mount",
    ".network",
    ".netdev",
    ".path",
    ".service",
    ".slice",
    ".socket",
    ".swap",
    ".target",
    ".timer"
]
KNOWN_UNITS_MUST_HAVE_UNITSECTION = [
    ".mount",
    ".service",
    ".socket",
    ".target"
]
KNOWN_RUNTIME_UNITS = [
    ".slice"
]

KNOWN_GENERATED_UNITS = [
    r".*\.mount",
    r".*\.swap",
    r"apport\.service",
    r"grub-common\.service",
    r"hddtemp\.service",
    r"systemd-cryptsetup@.*\.service",
    r"virtualbox\.service",
]