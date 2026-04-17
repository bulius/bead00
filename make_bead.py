"""
EDC Bead Generator — Blender Python script
Run with:  blender --background --python make_bead.py
Produces:  bead.blend  and  bead.stl  in the same directory as this script.

Approach: spin a closed 2-D cross-section profile 360° around the Z axis
(solid of revolution / lathe). This avoids Boolean operations entirely,
guaranteeing a through-hole, a manifold mesh, and clean topology.
"""

import bpy
import bmesh
import math
import os

# ---------------------------------------------------------------------------
# 0. Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(SCRIPT_DIR, "bead.blend")
STL_PATH   = os.path.join(SCRIPT_DIR, "bead.stl")

# ---------------------------------------------------------------------------
# 1. Fresh scene — metric millimetres
# ---------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.unit_settings.system       = 'METRIC'
scene.unit_settings.scale_length = 0.001   # 1 Blender unit = 1 mm
scene.unit_settings.length_unit  = 'MILLIMETERS'

# ---------------------------------------------------------------------------
# 2. Parameters (mm)
# ---------------------------------------------------------------------------
OUTER_R  = 6.0      # 12 mm outer diameter
INNER_R  = 2.25     # 4.5 mm hole diameter
HEIGHT   = 10.0
CHAMFER  = 0.6      # 45° chamfer on all four corners
SEGMENTS = 64       # spin resolution (number of radial slices)

# ---------------------------------------------------------------------------
# 3. Build closed 2-D cross-section profile in the XZ plane
#
#    The profile is the right-hand half of the bead cross-section,
#    listed counter-clockwise.  Each corner is replaced by two points
#    that form a straight 45° chamfer cut.
#
#    Z=HEIGHT ── [top outer chamfer] ── [top cap] ── [top inner chamfer]
#    Z=0      ── [bot inner chamfer] ── [bot cap] ── [bot outer chamfer]
# ---------------------------------------------------------------------------
profile = [
    # bottom inner corner (chamfer: ramps from cap into hole wall)
    (INNER_R + CHAMFER, 0.0),
    (INNER_R,           CHAMFER),
    # straight inner (hole) wall
    (INNER_R,           HEIGHT - CHAMFER),
    # top inner corner
    (INNER_R + CHAMFER, HEIGHT),
    # straight top cap (inner → outer)
    (OUTER_R - CHAMFER, HEIGHT),
    # top outer corner
    (OUTER_R,           HEIGHT - CHAMFER),
    # straight outer wall
    (OUTER_R,           CHAMFER),
    # bottom outer corner
    (OUTER_R - CHAMFER, 0.0),
    # closing edge back to first point = straight bottom cap (outer → inner)
]

# ---------------------------------------------------------------------------
# 4. Spin the profile 360° around the Z axis
# ---------------------------------------------------------------------------
mesh = bpy.data.meshes.new("BeadMesh")
bm   = bmesh.new()

verts = [bm.verts.new((x, 0.0, z)) for x, z in profile]

# Close the profile loop
for i in range(len(verts)):
    bm.edges.new((verts[i], verts[(i + 1) % len(verts)]))

geom = bm.verts[:] + bm.edges[:]
bmesh.ops.spin(
    bm,
    geom=geom,
    axis=(0, 0, 1),
    cent=(0, 0, 0),
    angle=math.radians(360),
    steps=SEGMENTS,
    use_merge=True,        # welds last ring back to first (closes the solid)
    use_normal_flip=False,
)

# ---------------------------------------------------------------------------
# 5. Mesh cleanup
# ---------------------------------------------------------------------------
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

bm.to_mesh(mesh)
bm.free()

# ---------------------------------------------------------------------------
# 6. Add to scene
# ---------------------------------------------------------------------------
obj = bpy.data.objects.new("Bead", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Smooth curved surfaces; keep flat caps flat
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))

# ---------------------------------------------------------------------------
# 7. Save .blend
# ---------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved: {BLEND_PATH}")

# ---------------------------------------------------------------------------
# 8. Export .stl
# ---------------------------------------------------------------------------
bpy.ops.wm.stl_export(
    filepath=STL_PATH,
    export_selected_objects=True,
    global_scale=1.0,      # coords are already in mm
    ascii_format=False,
)
print(f"Exported: {STL_PATH}")
print("Done — EDC bead ready for slicing.")
