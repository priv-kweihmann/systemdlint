KNOWN_PATHS = [
    "/etc/systemd/*",
    "/etc/systemd/**/*",
    "/lib/systemd/*",
    "/lib/systemd/**/*",
    "/run/systemd/*",
    "/run/systemd/**/*",
    "/usr/lib/systemd/*",
    "/usr/lib/systemd/**/*",
]

KNOWN_DROPIN_PATHS = {
    "user.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    "system.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".service": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".target": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".mount": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".automount": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".device": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".swap": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".path": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".timer": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".scope": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".slice": [
        "/etc/systemd/system/%unit%.d/*.conf", "/run/systemd/system/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    ".network": [
        "/etc/systemd/network/%unit%.d/*.conf", "/run/systemd/network/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    "logind.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    "timesyncd.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ],
    "journald.conf": [
        "/etc/systemd/%unit%.d/*.conf", "/run/systemd/%unit%.d/*.conf", "/usr/lib/systemd/%unit%.d/*.conf", "/lib/systemd/%unit%.d/*.conf"
    ]
}