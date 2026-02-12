# Violet 🟣

Violet is a **terminal file manager** written in Python, featuring a simple and modern interface using Rich. It allows you to navigate folders and files directly from the terminal, starting in your **HOME directory** by default.

---

## Installation

### Debian / Ubuntu

## 1. Download the latest `.deb` package:
wget https://github.com/pabloribet/violet/releases/download/v0.1.0/Violet-deb.deb

## 2. Install the package
sudo apt install ./Violet-deb.deb

## 3. If there is an dependence issue
sudo apt -f install

## 4. Run the package
violet

### Arch Linux / Manjaro

## Install dependencies:

sudo pacman -S python python-rich


## Install via PKGBUILD:

git clone https://github.com/pabloribet/violet
cd violet/violet-pkg
makepkg -si


## Run:

violet


## Optional: You can install the .deb on Arch using dpkg:

sudo pacman -S dpkg
sudo dpkg -i Violet-deb.deb

## Usage

Arrow keys ↑ ↓ to navigate

d > to delete files

m > to move

c > to copy

p > to paste

r > Rename files and folders

Enter > Open folder or file

q > Exit Violet

## The default starting folder is always the user's HOME directory.

## Updates

For new versions:

## Debian / Ubuntu:

wget https://github.com/pabloribet/violet/releases/download/v0.1.0/Violet-deb.deb
sudo apt install ./Violet-deb.deb


## Arch / Manjaro:

cd violet/violet-pkg
git pull
makepkg -si

Contributing

Contributions are welcome! Open issues or pull requests on GitHub.


