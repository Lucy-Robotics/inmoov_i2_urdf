# InMoov i2 (this package)

## What this repository implements today

**`inmoov_i2_urdf`** ships the **InMoov i2** robot description under `description/robot_description/`, vendored from [Artur-Fedjukevits/inmoov_ros2](https://github.com/Artur-Fedjukevits/inmoov_ros2/tree/main/src/inmoov_description) (`src/inmoov_description`, commit `73c584b`). Mesh URIs were rewritten from `package://inmoov_description/meshes/` to the parent `mesh_dir`; `description/urdf/inmoov.urdf.xacro` adds a fixed `base_node` root above the i2 `stand_link`. Meshes are CC BY-NC 4.0 (see `description/robot_description/LICENSE-ASSETS.md`).

`configs/default.yaml` is a generic starting point laid out like the InMoov i1 package: three boards, **`rp2040_left_arm`**, **`rp2040_right_arm`** and **`rp2040_torso_head`**, every actuator a 180° servo with the 0..π travel, `scale` 1, and an `offset` that puts the joint's lower URDF limit at 0 (its upper limit for the mirrored right shoulder and wrist). Every row is disabled, so the package runs in mock, RViz and Gazebo without hardware. The PoC robot's two-Mega wiring and calibration are in `configs/PoC_InMoovI2.yaml`, its poses on the `robot/poc` branch. To drive a robot, set each board's `serial_id` and pins to its wiring, activate the config in the LCP, then calibrate each joint and enable it once it is checked on the robot.
