# Developer guide — `inmoov_i2_urdf`

ROS 2 **Jazzy** (Ubuntu 24.04). For contributors who change URDF/xacro, meshes, RViz config, hardware YAML, or launch files. Bringup, hardware plugin, and cameras live in **`lucy_ros_packages`** ([Lucy-Robotics/lucy_ros_packages](https://github.com/Lucy-Robotics/lucy_ros_packages) → `docs/DEVELOPER.md`).

---

## 1. Role of this package

| Concern | Lives in |
|---------|----------|
| Robot description (xacro, meshes, materials, joint limits, collisions) | `description/` |
| ros2_control hardware interfaces (real / sim / mock) | `description/ros2_control/` |
| Gazebo (gz-sim) physics tuning + generated plugin/sensors | `description/gazebo/` (`inmoov_gazebo_physics.xacro`, generated `gazebo.xacro`, `gazebo_bridge.yaml`) |
| Hardware mapping (boards, actuators, sensors) | `config/hardware/active.yaml` — see [hardware_mapping.md](hardware_mapping.md) |
| Controller parameters for this package's bringup | `config/controllers.yaml` |
| RViz saved layout | `config/inmoov_rviz.rviz` |
| Launches (RViz, gz-sim, control, preview) | `launch/` |
| Lineage / archive | `archive/` (original InMoov-i1 STL set + URDF + PDF — not loaded at runtime) |

For the i2 boards and wiring, see [inmoov_i2.md](inmoov_i2.md).

---

## 2. Layout

```text
inmoov_i2_urdf/
├── package.xml / CMakeLists.txt
├── docs/                         # this file, hardware_mapping.md, inmoov_i2.md
├── launch/                       # 5 entry points (see §4)
├── config/                       # controllers.yaml, RViz config, hardware/*.yaml
├── description/
│   ├── urdf/inmoov.urdf.xacro    # top-level entry
│   ├── robot_description/
│   │   ├── urdf/properties.xacro          # model_scale (single source of truth)
│   │   ├── urdf/robot_description.urdf.xacro
│   │   └── meshes/dae/                    # 290 Collada meshes, every <visual> + <collision> uses one
│   ├── ros2_control/             # hardware interfaces + gz_ros2_control bridge
│   └── gazebo/                   # sim-only physics overrides
├── worlds/default.sdf            # used by gazebo.launch.py
├── test/                         # pytest suite (run via colcon test)
└── archive/                      # original InMoov assets (lineage; not installed for runtime)
```

---

## 3. Build and install

`CMakeLists.txt` installs `launch/`, `config/`, `description/`, `docs/`, `worlds/` to `share/inmoov_i2_urdf/`. Launches resolve paths from `get_package_share_directory("inmoov_i2_urdf")`.

```bash
colcon build --symlink-install --packages-select inmoov_i2_urdf lucy_ros2_control
source install/setup.bash
```

`--symlink-install` makes edits to `description/`, `launch/` and `config/` effective on the next `ros2 launch` — rebuild only after changes to `CMakeLists.txt`, `package.xml`, `test/`, or files outside the installed directories.

No `package.xml` dependency on `lucy_ros2_control` (would cycle: `lucy_ros2_control` depends on this URDF). Keep both packages in the same workspace; combo launches still need `lucy_ros2_control` at runtime.

---

## 4. Launch files

| Launch | What it starts | Typical use |
|--------|----------------|-------------|
| `control.launch.py` | `lucy_control_supervisor` → `robot_state_publisher` + `ros2_control_node` + controller spawners. **Real hardware path** (or `use_mock_hardware:=true`). | Bench / Lucy bringup without the panel. |
| `gazebo.launch.py` | `gz sim`, `/clock` + camera bridges, `create` to spawn the robot, `gz_ros2_control` plugin path, controller spawners. | Standalone Gazebo session. |
| `joint_preview.launch.py` | `robot_state_publisher` + `joint_state_publisher_gui` + RViz. | Sweep URDF `<limit>` values with sliders, validate collisions visually. |
| `rviz.launch.py` | RViz2 only. Forwarded by `lucy_bringup` when `rviz:=true`. | Already covered by full bringup. |
| `rviz_standalone.launch.py` | RViz2 only. | Second-terminal view when another stack publishes `/robot_description` + `/joint_states`. |

Common arguments are listed in the root [README.md](../README.md#quick-launches).

---

## 5. Xacro architecture

`description/urdf/inmoov.urdf.xacro` is the **only entry point**. Top-level arguments and includes:

```xml
<xacro:arg name="base_path"        default="."/>
<xacro:arg name="use_gazebo_sim"   default="false"/>
<xacro:arg name="use_mock_hardware" default="false"/>
<xacro:arg name="controller_config" default=""/>

<xacro:include filename="../robot_description/urdf/properties.xacro"/>
<xacro:include filename="../robot_description/urdf/robot_description.urdf.xacro"/>

<!-- real / mock hardware only; Gazebo provides its own gz_ros2_control via gazebo.xacro -->
<xacro:unless value="$(arg use_gazebo_sim)">
  <xacro:include filename="../ros2_control/inmoov_ros2_control.xacro"/>
</xacro:unless>

<xacro:if value="$(arg use_gazebo_sim)">
  <xacro:include filename="../gazebo/inmoov_gazebo_physics.xacro"/>
  <xacro:include filename="../gazebo/gazebo.xacro"/>
</xacro:if>
```

| File | Responsibility |
|------|---------------|
| `robot_description/urdf/properties.xacro` | `model_scale` xacro property — the **single** length-scale knob. Multiplies every joint/visual/collision `<origin xyz>` and primitive size in the body URDF. |
| `robot_description/urdf/robot_description.urdf.xacro` | Links, joints, visuals (`<mesh>`), collisions (`<mesh>` or primitive), inertias, named `<material>` definitions, and `<material name="…"/>` refs on visuals. |
| `robot_description/meshes/dae/*.dae` | Collada meshes — used by **all three renderers** as the visual mesh (Gazebo also as the source of `<diffuse>` colour for mesh visuals, see §6). |
| `ros2_control/inmoov_ros2_control.xacro` | `<ros2_control>` block: selects `gz_ros2_control/GazeboSimSystem` (Gazebo) or `lucy_ros2_control/LucySystemHardware` (real + mock — `publish_actuators:=false` toggles the micro-ROS publisher off in mock). Each `<command_interface name="position">` carries `<param name="min/max">` from the URDF `<limit>`; `LucySystemHardware` clamps to that envelope. The stock `gz_ros2_control` plugin in this workspace does **not** apply the clamp. |
| `gazebo/gazebo.xacro` | gz-sim only — **generated by `lucy_config_generator`**. Declares the `gz_ros2_control` system plugin (so `controller_manager` runs inside Gazebo) plus the simulated camera sensors. Replaces the old hand-written `inmoov_gz_ros2_control.xacro`. |
| `gazebo/gazebo_bridge.yaml` | gz-sim only — **generated** `ros_gz_bridge` config mapping gz topics to ROS topics (clock, camera images, sensor arrays). `gazebo.launch.py` republishes the raw camera topics into the compressed topics declared under `cameras:` in `active.yaml`. |
| `gazebo/inmoov_gazebo_physics.xacro` | gz-sim only — `<static>` on the stand, body/hand friction (`mu1/mu2`), contact stiffness (`kp/kd`), `self_collide` flags. **No colours** (see §6). |

Editing joint names or interfaces requires updating **all three** in lockstep: `inmoov_ros2_control.xacro`, `config/controllers.yaml`, `config/hardware/active.yaml`. The hardware → ros2_control generation lives in `lucy_config_generator`.

---

## 6. Editing the URDF

### 6.1 `model_scale`

Single number in `description/robot_description/urdf/properties.xacro`. Current `0.10604` gives the measured crown height of 1.81 m. Every joint/visual/collision position, primitive size and `<mesh scale>` in the body URDF is multiplied by it; **never** scale individual visuals — change this value instead. Inertials are in SI for this scale and must be re-estimated when it changes.

### 6.2 Adding / removing a link or joint

1. Edit `robot_description.urdf.xacro`. Wrap every new joint/visual/collision `<origin xyz="…">` and primitive size in `${model_scale * N}`. Leave `<inertial>` origins in SI.
2. If the visual has a mesh, also write a paired `<collision>` (same origin + mesh).
3. Pick or define a `<material name="Material.NNN">` and reference it on the new `<visual>` so RViz / LCP get a colour.
4. Update `config/hardware/active.yaml` and `config/controllers.yaml` if the new joint is actuated (then regenerate via `lucy_config_generator`).
5. Validate: `colcon test --packages-select inmoov_i2_urdf` (xacro smoke + collisions present + joint limits) and `joint_preview.launch.py`.

### 6.3 Replacing a mesh

Drop the new `.dae` into `description/robot_description/meshes/dae/` and point the existing `<mesh filename="${mesh_dir}/…dae"/>` at it. Keep `mesh scale="${model_scale*1} …"` — the file scale stays uniform with `model_scale`.

Pitfalls to avoid (seen in past Gazebo crashes):

- DAEs containing **`<lines>` primitives** with zero normals make gz-sim segfault in DARTsim. Strip `<lines>` blocks before committing or refuse line-only meshes.
- Unreferenced DAEs are not picked up by anything but bloat the install; clean up orphans after edits.

### 6.4 Materials and how each viewer reads them

The same model is rendered by three things; they do **not** use the same colour source:

| Viewer | Colour source | Notes |
|--------|---------------|-------|
| **RViz** | URDF `<material name="X"><color rgba="…"/></material>` referenced on the visual. | Single colour per visual. |
| **LCP** (Three.js, TEXTURE on) | Embedded Collada `<effect>` / `<diffuse>` inside each `.dae`, per submesh. | Multiple sub-materials per DAE are honoured. |
| **Gazebo (gz-sim)** | Embedded Collada `<diffuse>` of mesh visuals — URDF `<material>` is **ignored** for mesh `<visual>`. | Mirrors LCP by construction. |

Practical consequences:

- Changing only the URDF `<material>` changes RViz, **not** Gazebo or LCP.
- A DAE with default-black `<diffuse>` will show black in Gazebo even if RViz looks right.
- Adding per-visual `<gazebo reference="LINK"><visual name="…"><material>…</material></visual></gazebo>` overrides is brittle in gz-sim 6 (named-vs-anonymous mismatches silently no-op). The supported lever is **the DAE itself**.
- Keep the three views consistent by either re-exporting the DAE with the desired diffuse, or by editing the URDF material **and** rewriting the `<diffuse>` entries in the DAE in lockstep.

### 6.5 Joint limits

Limits are per-joint, in radians, on the `<limit lower="…" upper="…"/>` of each actuated joint in `robot_description.urdf.xacro`. They are **decoupled** from `config/hardware/active.yaml`: the hardware mapping handles servo↔URDF conversion (`offset_deg`, `direction`, `scale` — see [hardware_mapping.md](hardware_mapping.md)).

`lucy_config_generator` copies the `<limit lower upper>` of every actuated joint into the `<command_interface name="position">` block of the regenerated `inmoov_ros2_control.xacro` as `<param name="min/max"/>` (radians). At runtime, `LucySystemHardware` clamps `hw_commands_` to that envelope before the actuator mapping. Stock `gz_ros2_control` does **not** apply this clamp; rely on URDF `<limit>` enforcement coming from the spawned model when running in Gazebo.

See §7.

---

## 7. Calibration workflow

Two independent concerns: **collisions** (rarely revisited once correct) and **joint limits** (per joint, by hand).

### 7.1 Collisions

Strategy is **all-mesh, per-visual**: every `<visual><mesh/>` in every link gets a paired `<collision>` reusing the same origin + mesh. Multi-mesh body links (`torso_y_link` with ~80 sub-DAEs) collide as the full visual hull. Hand-authored primitives on root frames (`base_node`, `stand_link`) are preserved.

Workflow:

1. **Manual edit** — hand-author `<collision>` blocks in `robot_description.urdf.xacro`, mirroring the matching `<visual>` origin + mesh filename, or use a primitive (`<box>`, `<cylinder>`, `<sphere>`) when a mesh is overkill. Wrap dimensions in `${model_scale * N}`.
2. **Visual check**:
   ```bash
   ros2 launch inmoov_i2_urdf joint_preview.launch.py
   ```
   The default RViz config has two `RobotModel` displays — opaque visual + translucent collision overlay. Toggle the visual off to see only collisions (what PyBullet / Gazebo will see); raise alpha for clarity. Drive joints with the sliders and look for:
   - collisions that don't hug the mesh (DAE artefact),
   - non-adjacent links interpenetrating at neutral pose,
   - missing collisions on links you care about.

### 7.2 Joint limits — by hand (preferred for actuator end-stops)

1. Power off the motors, back-drive the real joint to each mechanical extreme.
2. Read off the URDF angle (mind the joint-axis sign).
3. Edit the matching `<limit lower="…" upper="…"/>` in `robot_description.urdf.xacro`. Add a trailing `<!-- = X deg .. Y deg -->` comment for readability.
4. Reload:
   ```bash
   # Quick slider preview
   ros2 launch inmoov_i2_urdf joint_preview.launch.py
   # OR in a running stack, without relaunching
   ros2 service call /lucy_control/restart std_srvs/srv/Trigger {}
   ```

### 7.3 Integrated check (Gazebo + RViz)

After calibration, validate in the full stack:

```bash
# Mock-hardware path (LucySystemHardware with publish_actuators:=false; no Gazebo, no real motors)
ros2 launch lucy_bringup lucy.launch.py robot_package:=inmoov_i2_urdf real:=false rviz:=true

# Headless Gazebo (server-only with EGL rendering — camera sensors keep producing frames)
ros2 launch lucy_bringup lucy.launch.py robot_package:=inmoov_i2_urdf gazebo:=true headless:=true

# Gazebo with GUI + RViz (X11 required)
ros2 launch lucy_bringup lucy.launch.py robot_package:=inmoov_i2_urdf gazebo:=true rviz:=true
```

Hot-reload after editing the URDF:

```bash
ros2 service call /lucy_control/restart std_srvs/srv/Trigger {}
```

This restarts `robot_state_publisher` + `ros2_control` with the new URDF. **Caveat**: when the ros2_control topology changes (joints added/removed, hardware system swapped), Gazebo must be **relaunched** — `gz_ros2_control` loads once at world spawn and does not re-read.

---

## 8. Hardware mapping (pointer)

`config/hardware/active.yaml` is the **single source of truth** for boards, actuators, sensors, and the URDF↔servo calibration (`offset_deg`, `direction`, `scale`). The schema, semantics, and validation rules live in [hardware_mapping.md](hardware_mapping.md). The control panel and `lucy_config_generator` write here; never hand-edit during a running pipeline.

Named presets under `config/hardware/configs/` are snapshots; `config/hardware/active_meta.yaml` records which preset is active and whether it was flashed.

For the i2 boards and wiring, see [inmoov_i2.md](inmoov_i2.md).

---

## 9. Tests

```bash
colcon build --symlink-install --packages-select inmoov_i2_urdf lucy_ros2_control \
  --cmake-args -DBUILD_TESTING=ON
colcon test --packages-select inmoov_i2_urdf --event-handlers console_direct+
colcon test-result --verbose
```

| Test | What it checks |
|------|----------------|
| `test_xacro_smoke.py` | `inmoov.urdf.xacro` expands cleanly with default args and with `use_gazebo_sim:=true`. |
| `test_joint_limits.py` | Every actuated joint has a `<limit>` and limits are within plausible ranges. |
| `test_collisions_present.py` | Every `<visual><mesh/>` has a matching `<collision>`. |
| `test_model_scale.py` | Every mesh scale and non-inertial `<origin xyz>` uses `${model_scale}`. |
| `test_hardware_yaml.py` | `active.yaml` schema, board references, virtual-pin contiguity, etc. |

CI (`.github/workflows/ci.yml`) runs the same tests, then `pytest-cov` for `test/` only, and uploads Cobertura XML + HTML to Codecov (flag `inmoov_i2_urdf`) when `CODECOV_TOKEN` is set. Triggers: PRs and pushes to `main` / `master` / `dev`.

---

## 10. RViz

- Layout: `config/inmoov_rviz.rviz` — opaque `RobotModel (Visual)` + translucent `RobotModel (Collision)` overlay. Pin RViz version expectations in release notes if the file breaks across upgrades.
- TF chain: `joint_state_broadcaster` → `/joint_states` → `robot_state_publisher` → TF → `RobotModel`.

---

## 11. Extension checklist

1. **New link / joint / mesh** — update the xacro, add the paired `<collision>`, run the test suite. Pick or define a `<material>` (RViz colour).
2. **New ros2_control joint** — edit `inmoov_ros2_control.xacro`, `config/hardware/active.yaml`, and `config/controllers.yaml` together (and firmware via the generator).
3. **New launch argument** — propagate to `lucy_bringup` if integrators set it; document in this file and the root README.
4. **New mesh** — verify it has triangle geometry (no `<lines>`-only) and reasonable `<diffuse>` for Gazebo.
5. **Licensing** — InMoov-derived assets keep their CC BY-NC 4.0 attribution; add new sources to the package `LICENSE` / `ATTRIBUTION.md` notes.

---

## 12. Contributing

The root `CONTRIBUTING.md` carries the GPL-3.0 "contributing" wording expected by `ament_copyright`; `LICENSE` is at the root.

- Open issues and merge requests on the host for this repository.
- Match ROS 2 / ament style; run `colcon test --packages-select inmoov_i2_urdf` before submitting.
- Update this guide or the root `README.md` whenever the layout or workflow changes.

See `CODE_OF_CONDUCT.md` at the repository root.
