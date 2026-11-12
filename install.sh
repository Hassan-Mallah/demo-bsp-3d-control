#!/usr/bin/env bash
set -eu

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    echo "This script must be run as root (or with sudo)."
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This installer expects a Debian/Ubuntu-based system with apt-get."
    exit 1
fi

ensure_pkg() {
    local pkg="$1"
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        echo "Installing package: $pkg"
        apt-get update
        apt-get install -y "$pkg"
    else
        echo "Package already installed: $pkg"
    fi
}

ensure_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Installing Python 3"
        apt-get update
        apt-get install -y python3
    else
        echo "Python 3 already installed"
    fi

    if ! command -v python >/dev/null 2>&1; then
        echo "Creating python symlink to python3"
        ln -sf /usr/bin/python3 /usr/local/bin/python
    fi
}

ensure_python
ensure_pkg "python3-pip"
ensure_pkg "git"
ensure_pkg "gpiod"

if ! python -m pip --version >/dev/null 2>&1; then
    echo "pip is not available for python. Please check the Python installation."
    exit 1
fi

echo "Upgrading pip"
python -m pip install --upgrade pip

echo "Installing Flask"
python -m pip install --no-cache-dir flask

echo "Installing gpiod Python bindings"
python -m pip install --no-cache-dir gpiod

echo "Installation complete."
