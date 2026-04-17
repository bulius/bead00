# panda_bead_01 — Change Summary

## Overview
Developed a 3D-printable EDC bead with a panda face carved into its outer surface, built on top of the clean cylindrical bead from `bead.blend`.

## Files

| File | Description |
|------|-------------|
| `panda_bead.blend` | Main working file — contains all objects (see below) |
| `panda_bead_01.blend` | Isolated file with `Bead` + `panda_bead_intersection_v2` only |
| `panda_extruded.blend` | Source panda face — flat extruded mesh |
| `panda_extruded_smoothed.blend` | Smoothed variant of panda face |
| `panda_extruded.stl` | STL export of source panda face |

## Objects in `panda_bead.blend`

| Object | Description |
|--------|-------------|
| `Bead` | Clean spin-built cylindrical bead (12mm OD, 10mm H, 4.5mm hole, 0.6mm chamfers) |
| `Bead.001` | Duplicate of Bead, used as Boolean base |
| `Panda` | Flat extruded panda face mesh, positioned at bead front face |
| `panda_minus_bead` | Panda shape with bead volume subtracted (Boolean cutter reference) |
| `panda_bead_carved` | **Primary output** — Bead with panda face carved into outer surface |
| `panda_cutter` | Helper object used for Boolean carve (hidden) |

## Methodology: `panda_bead_carved`

The panda face was carved into the bead outer surface using a **Boolean DIFFERENCE** workflow optimised for FDM 3D printing:

1. **Pre-triangulate** base bead mesh (Beauty method) before Boolean
2. **Boolean DIFFERENCE** using `Panda` as cutter (Exact solver)
   - Carve depth: ~2.24mm at center (exceeds 1.5mm minimum for clear print readability)
   - Cutter transforms applied before use to ensure clean geometry
3. **Post-cleanup:**
   - Merge doubles (threshold 0.0001mm) — removed 1 duplicate vertex
   - Triangulate 133 residual ngons
   - Recalculate face normals
   - Shade Smooth by Angle (30°)
4. **Validation result:** 1407 verts, 2470 faces, 0 ngons, 0 non-manifold edges, 0 boundary edges, Euler characteristic = 0 (correct torus topology — watertight)

## Print Notes
- Material: any FDM filament (PLA, PETG, etc.)
- Nozzle: 0.4mm recommended
- The carved panda face is on the +Y side of the bead (front face)
- Carve depth of ~2.24mm provides strong shadow contrast for clear feature definition
- Through-hole (4.5mm) sized for standard paracord
