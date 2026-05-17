#!/bin/bash
# ============================================================
#  install_taudem.sh — Compila e installa TauDEM su Linux
#  Testato su Ubuntu con GCC 15, CMake 4.x, GDAL 3.12
# ============================================================

set -e

echo "============================================"
echo " Installazione TauDEM"
echo "============================================"

# --- 1. Dipendenze di sistema ---
echo "[1/5] Installazione dipendenze..."
sudo apt install -y cmake openmpi-bin libopenmpi-dev libgdal-dev git

# --- 2. Clona il repository ---
echo "[2/5] Download TauDEM..."
cd ~
git clone https://github.com/dtarb/TauDEM.git
cd TauDEM/src

# --- 3. Fix CMakeLists.txt (manca cmake_minimum_required) ---
echo "[3/5] Fix CMakeLists.txt..."
sed -i '1s/^/cmake_minimum_required(VERSION 3.10)\n/' CMakeLists.txt

# --- 4. Configura con cmake ---
echo "[4/5] Configurazione cmake..."
mkdir -p build && cd build
cmake ..

# Fix flag -flto incompatibili con questo GCC/GDAL
# (GDAL inietta -flto=auto -ffat-lto-objects che GCC non accetta in questo contesto)
find . -name "flags.make" -exec sed -i \
    's/-flto=auto -ffat-lto-objects//g; s|"-flto=auto -ffat-lto-objects"||g; s|""||g' {} \;
find . -name "link.txt" -exec sed -i \
    's/-flto=auto -ffat-lto-objects//g' {} \;
find . -name "link.txt" -exec sed -i \
    's|"-flto=auto -ffat-lto-objects"||g' {} \;

# --- 5. Compila e installa ---
echo "[5/5] Compilazione e installazione..."
make -j$(nproc)
sudo make install

echo ""
echo "============================================"
echo " TauDEM installato con successo!"
echo ""
echo " Verifica con:"
echo "   mpiexec -n 1 pitremove"
echo "============================================"
