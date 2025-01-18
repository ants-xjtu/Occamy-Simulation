# Reproducing Results from the Paper

This document provides instructions on how to reproduce the main experimental results (Figures 6, 14, 15, 16, and 17) presented in our paper using the **Occamy-Simulation** codebase.

## Prerequisites

1. **ns-3 Environment**

   - Clone (or otherwise acquire) the **Occamy-Simulation** repository:

     ```bash
     git clone https://github.com/ants-xjtu/Occamy-Simulation.git
     ```

   - Build and configure ns-3 with the required profile and options:

     ```bash
     cd Occamy-Simulation/ns-3/
     ./ns3 configure --build-profile=optimized --enable-examples --enable-tests
     ```

   - After building, navigate to the Occamy directory:

     ```bash
     cd Occamy-Simulation/ns-3/examples/Occamy/
     ```

   All commands below assume you are inside this `Occamy` directory.

------

## Figure 6. CDF of Buffer/Memory Bandwidth Utilization

1. **Run the simulation**

   ```bash
   bash run-100g_utilization.sh
   ```

   This script will run the simulation scenario(s) needed to generate the data.

2. **Post-process / Generate the figure**

   ```bash
   python get_cdf_utilization.py
   ```

   This script reads the output of the simulation and plots the CDF of buffer (or memory) bandwidth utilization.

3. **Result**
   The resulting figures will appear under:

   ```bash
   figure/utilization/
   ```

------

## Figure 14. QCT and FCT under Benchmark Traffic

1. **Run the simulation**

   ```bash
   bash run-100g_benchmark.sh
   ```

2. **Post-process**

   ```bash
   python get_slowdown_benchmark.py
   ```

   This script calculates slowdowns, QCT, and FCT from the simulation output.

3. **Result**
   The figure and related data will be in:

   ```bash
   figure/100g_benchmark/
   ```

------

## Figure 15. Performance with All-to-All Traffic

1. **Run the simulation**

   ```bash
   bash run-100g_alltoall.sh
   ```

2. **Post-process**

   ```bash
   python get_slowdown_alltoall.py
   ```

3. **Result**
   The figure and related data will be in:

   ```bash
   figure/100g_alltoall/
   ```

------

## Figure 16. Performance with All-Reduce Traffic

1. **Run the simulation**

   ```bash
   bash run-100g_allreduce.sh
   ```

2. **Post-process**

   ```bash
   python get_slowdown_allreduce.py
   ```

3. **Result**
   The figure and related data will be in:

   ```bash
   figure/100g_allreduce/
   ```

------

## Figure 17. Performance with Higher Query Traffic Load

1. **Run the simulation**

   ```bash
   bash run-100g_queryload.sh
   ```

2. **Post-process**

   ```bash
   python get_slowdown_queryload.py
   ```

3. **Result**
   The figure and related data will be in:

   ```bash
   figure/100g_allreduce/
   ```

------

