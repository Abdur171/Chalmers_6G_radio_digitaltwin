# Digital Radio Twin of Chalmers for 6G Integrated Sensing, Positioning, and Communication

[![Institution](https://img.shields.io/badge/Institution-Chalmers%20University%20of%20Technology-005B94.svg)](https://www.chalmers.se/)
[![Degree Project](https://img.shields.io/badge/Degree%20Project-EENX16%20Electrical%20Engineering-FFB81C.svg)](#academic-attribution)
[![Ray Tracing](https://img.shields.io/badge/Engine-Sionna%20RT%20v1.0.2-76B900.svg)](https://nvlabs.github.io/sionna/rt/index.html)
[![3D Modeling](https://img.shields.io/badge/3D%20Modeling-Blender%203.6%20LTS-F5792A.svg)](https://www.blender.org/)
[![Analysis](https://img.shields.io/badge/KPI%20Analysis-MATLAB%20R2024a-ED8B00.svg)](https://se.mathworks.com/)
[![License](https://img.shields.io/badge/License-Academic%20Research-blue.svg)](#license)

An end-to-end computational pipeline and physical 3D electromagnetic propagation dataset for **6G Integrated Sensing and Communication (ISAC)** and **Digital Radio Twins**. Built using NVIDIA's GPU/CPU-accelerated [Sionna RT](https://nvlabs.github.io/sionna/rt/index.html) ray-tracing framework, high-fidelity [Blender 3D](https://www.blender.org/) geometric models, and OpenStreetMap GIS terrain data, this project models the complete Johanneberg campus of Chalmers University of Technology down to sub-meter physical material specifications.

---

## Visual Showcase

<div align="center">
  <img src="https://github.com/user-attachments/assets/652113af-5001-476f-b1a9-9d19d4f25775" alt="Chalmers Entrance Map 3D" width="48%"/>
  <img src="https://github.com/user-attachments/assets/a2b92252-ce6e-4bd5-b663-fda5a6dab4dc" alt="Entrance Close-up Ray Tracing" width="48%"/>
</div>
<div align="center">
  <img src="https://github.com/user-attachments/assets/d3a9e27d-cfa3-4ff7-839c-83bab320b103" alt="3D Height Grid and Multipath" width="48%"/>
  <img src="https://github.com/user-attachments/assets/f270e5c5-88a3-4a7c-927f-c951860a3036" alt="Full Chalmers Digital Radio Twin" width="48%"/>
</div>

---

## Architectural Pipeline

```
  OpenStreetMap / GIS Data
            │
            ▼
┌───────────────────────────────┐
│     Blender 3D Modeling       │  ◄── BLOSM Terrain & Building Ingestion
│   - Material Assignment       │  ◄── Custom Radio Dielectrics (ITU-R)
│   - UE Grid Positioning Mesh  │  ◄── Python Procedural Placement
└───────────────┬───────────────┘
                │ Mitsuba XML Exporter (Y-Forward, Z-Up)
                ▼
┌───────────────────────────────┐
│       Sionna RT Engine        │  ◄── 6 Multi-Antenna Base Stations (MIMO)
│   - Shooting & Bouncing Rays  │  ◄── Specular, Diffuse & Refraction Paths
│   - Doppler, Delay, AoA / AoD │  ◄── Carrier Frequency fc = 3.5 GHz
└───────────────┬───────────────┘
                │ Structured Handoff
                ▼
┌───────────────────────────────┐
│   Structured Dataset Storage  │  ──► a_coeffs.csv (Complex Gains)
│     (25,000+ Path Metrics)    │  ──► h_frequency.csv (Channel Frequency Response)
└───────────────┬───────────────┘  ──► other_params.csv (Delay, Doppler, Angles)
                │                  ──► vertices.csv (3D Multipath Bounce Vertices)
                ▼
┌───────────────────────────────┐
│   MATLAB R2024a KPI Engine    │  ──► Cramér-Rao Lower Bound (CRLB) Positioning
│     (Sensing & Comm Metrics)  │  ──► Shannon Capacity & Latency Analysis
└───────────────────────────────┘
```

---

## Technical Specifications & Parameters

| Subsystem | Parameter | Configuration / Value |
|-----------|-----------|-----------------------|
| **Carrier Frequency ($f_c$)** | Center Frequency | 3.50 GHz (Mid-band 5G/6G) |
| **Wavelength ($\lambda$)** | Physical Wavelength | 8.57 cm |
| **Base Stations (BS)** | Total Transmitters ($T_x$) | 6 Multi-Sector Towers distributed across campus |
| **Transmitter Array** | Geometry & Polarization | $2 \times 2$ Planar Uniform Array ($\lambda/2$ spacing), Vertical Polarization |
| **User Equipment (UE)** | Grid Discretization | 1.0 m $\times$ 1.0 m high-density spatial evaluation grid |
| **Propagation Engine** | Ray Tracing Algorithm | Shooting and Bouncing Rays (SBR) via Mitsuba / Dr.Jit |
| **Electromagnetic Properties** | Surface Materials | Concrete, glass, asphalt, foliage calibrated to ITU-R recommendations |
| **Data Volumes** | Rx Evaluation Nodes | 2,000+ receiver points sampled across entrance & campus zones |

---

## Repository Structure

```
Bachelor_Thesis_Chalmers_radio_digitaltwin/
├── Campus_XML/                  # Full Chalmers campus Mitsuba XML scene exports
├── Data/                        # Generated multipath propagation datasets
│   └── tx_1/ ... tx_6/          # Base station directories
│       └── rx_1/ ... rx_N/      # Per-UE channel coefficients and ray bounce data
├── Data_Generation/             # Sionna RT execution pipeline
│   ├── Data_Generation.py       # Main ray-tracing synthesis driver
│   ├── Code_validation.ipynb   # Interactive parameter verification notebook
│   ├── Entrance_XML/            # High-resolution focus scene for student union
│   └── Grids/                   # 1x1m spatial mesh coordinate generators
├── KPI_analysis/                # MATLAB scripts evaluating 6G ISAC performance
│   ├── CRLB_Positioning.m       # Cramér-Rao Lower Bound localization precision
│   └── Channel_Capacity.m       # Shannon spectral efficiency and coverage
├── Map/                         # 3D Source geometry & Blender project files
│   ├── Chalmers_map_full.blend  # Complete campus 3D geometry
│   ├── Chalmers_map_entrance.blend
│   └── Python code for Blender/ # Procedural mesh generators & coordinate exporters
└── Thesis/                      # Published bachelor thesis report and scientific poster
```

---

## Structured Dataset Schema

For each receiver node `rx_N`, the dataset provides four synchronized telemetry matrices:

1. **Complex Channel Coefficients (`a_coeffs.csv`)**:  
   $\mathbf{alpha} \in \mathbb{C}^{N{\text{paths}} \times (N{\text{tx\ant}} \times 2)}$.  
   Contains alternating real and imaginary components of path gains per antenna element.
2. **Channel Frequency Response (`h_frequency.csv`)**:  
   $\text{CFR} \in \mathbb{C}^{N{\text{subcarriers}} \times (N{\text{tx\ant}} \times 2)}$.  
   Wideband channel frequency response sampled over allocated OFDM subcarriers.
3. **Propagation Parameters (`other_params.csv`)**:  
   $\mathbf{P} \in \mathbb{R}^{N_{\text{paths}} \times 6}$.  
   Synchronous multipath attributes: propagation delay ($\tau$), Doppler shift ($\nu$), Azimuth AoA/AoD ($\phi_r, \phi_t$), and Zenith AoA/AoD ($\theta_r, \theta_t$).
4. **Multipath Reflection & Scattering Vertices (`vertices.csv`)**:  
   $\mathbf{V} \in \mathbb{R}^{(N_{\text{depth}} \times N_{\text{paths}}) \times 4}$.  
   Full 3D coordinate tracing $(x, y, z)$ of every physical specular/scattering interaction bounce point.

---

## Getting Started

### 1. Prerequisites
- Python 3.10.9
- NVIDIA GPU with CUDA 12+ (or CPU mode via Dr.Jit LLVM)
- Blender 3.6 LTS
- MATLAB R2024a (for KPI processing)

### 2. Environment Setup
```bash
git clone https://github.com/Abdur171/Bachelor_Thesis_Chalmers_radio_digitaltwin.git
cd Bachelor_Thesis_Chalmers_radio_digitaltwin

python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install tensorflow sionna matplotlib pandas numpy
```

### 3. Running Ray Tracing Synthesis
```bash
python Data_Generation/Data_Generation.py
```

### 4. Running KPI Analysis in MATLAB
```matlab
cd KPI_analysis
run('CRLB_Positioning.m')
```

---

## Academic Attribution

This research was developed as an official undergraduate degree project at **Chalmers University of Technology**, Gothenburg, Sweden:

- **Department**: Department of Electrical Engineering
- **Course**: `EENX16` — Degree Project in Electrical Engineering (Bachelor Thesis)
- **Academic Authors**:
  - Abdur Arshad
  - Antony Hamouche
  - Liping Bai
  - Ramtin Mobaraki
  - Malte Rylander
  - Jamal Abdi Jamal
- **Academic Supervisors**:
  - **Prof. Henk Wymeersch** (Professor of Communication Systems, Chalmers University of Technology)
  - **Christian Nelson** (Doctoral Researcher in Wireless Communication & ISAC)

---

## Citation & References

If you use this dataset or ray-tracing model in your research, please cite:
```bibtex
@bachelorthesis{chalmers_radio_digitaltwin_2024,
  author    = {Arshad, Abdur and Hamouche, Antony and Bai, Liping and Mobaraki, Ramtin and Rylander, Malte and Abdi, Jamal},
  title     = {Digital Radio Twin of Chalmers for 6G Integrated Sensing, Positioning, and Communication},
  school    = {Chalmers University of Technology},
  department= {Department of Electrical Engineering},
  year      = {2024},
  note      = {Supervised by Prof. Henk Wymeersch and Christian Nelson}
}
```
