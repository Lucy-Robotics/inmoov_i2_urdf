# InMoov i2 (this package)

## What this repository implements today

**`inmoov_i2_urdf`** ships the **InMoov i2** robot description under `description/robot_description/`, vendored from [Artur-Fedjukevits/inmoov_ros2](https://github.com/Artur-Fedjukevits/inmoov_ros2/tree/main/src/inmoov_description) (`src/inmoov_description`, commit `73c584b`). Mesh URIs were rewritten from `package://inmoov_description/meshes/` to the parent `mesh_dir`; `description/urdf/inmoov.urdf.xacro` adds a fixed `base_node` root above the i2 `stand_link`. Meshes are CC BY-NC 4.0 (see `description/robot_description/LICENSE-ASSETS.md`).

The hardware YAML drives the i2 from two Arduino Mega 2560 boards (`board_class: i2c_pwm_only`), each behind a Nervo board: **`mega_left`** (head on its PCA9685, left arm on the Nervo ribbon) and **`mega_right`** (both hands and wrists on two PCA9685s, 0x41 left / 0x40 right, plus the right arm and stomach on the Nervo ribbons). `pca_addresses` lists each board's chips; `physical_pin` N is PCA9685 output N-1 (17-32 on the second chip). Ribbon (direct Mega pin) servos are not supported yet and stay disabled placeholders. `configs/default.yaml` is a generic, all-disabled InMoov i2; the PoC robot's calibrated config and poses live on the `robot/poc` branch. Set each board's `serial_id` to its Mega's USB serial number, then activate the config in the LCP with the board selected (or `pixi run firmware-flash-mega <board>`): the firmware tables are generated from the YAML. The i2 **expression** joints (eyelids, cheeks, brows, forehead, upper lip) exist in the URDF but are not wired yet: the generator publishes them at 0 through `joint_state_broadcaster` `extra_joints`.

## How to add i2 head actuators to the YAML

1. **Freeze URDF joint names** in the description package (each DOF exactly one `joint name="..."` in the generated URDF).
2. For each servo on **`mega_left`**'s head PCA, append one list element to **`actuators:`** in `active.yaml` (or a preset under `configs/`).
3. Assign **`virtual_pin`** as **contiguous integers per board**, starting after the last existing actuator on that board (today, `0`..`11` are used on `mega_left`).
4. Set **`physical_pin`** to the PCA9685 channel (or equivalent) from your **actual** schematic. The appendix below uses **example** channels (jaw on **7**, cheeks **8-9**, and so on through **22**) typical of full InMoov-style head wiring. Many draft tables also put “head roll” on **physical_pin 6**, which **collides** with the pins already used on `mega_left`-treat the appendix as a **template**, then renumber every `physical_pin` to match the board you build.
5. Tune **`servo_*_rad`**, **`offset_rad`**, **`direction`**, and **`scale`** on the bench once the joint exists in ros2_control.

## Appendix - example YAML: i2-oriented head / expression actuators

Paste the list items at the end of the top-level **`actuators:`** sequence in `active.yaml` (or merge a preset) once the URDF exposes matching joints and each **`physical_pin`** is verified on the PCA.

**Pin conflict note:** If you follow common InMoov-style numbering, “head roll” often lands on **`physical_pin: 6`**, which collides with Lucy’s **`right_shoulder_y_joint`** on the same board (also pin **6**). The first row below uses **`physical_pin: 23`** as a stand-in for “move head roll to a free channel”; change it to match your PCB.

**`virtual_pin`:** Continue after the last actuator on `mega_left` (today **`0`** .. **`11`**). The appendix uses **`2` … `18`**.

**`urdf_joint`:** every row matches a joint in the current `description/robot_description` tree.

```yaml
# Append under the top-level key `actuators:` (not as a nested document).
  - id: i2_head_roll_neck
    urdf_joint: neck_joint
    board: mega_left
    virtual_pin: 2
    physical_pin: 23
    servo_type: "270"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 4.71239
    servo_default_rad: 2.35619
    enabled: false

  - id: i2_jaw
    urdf_joint: i02_head_jaw_joint
    board: mega_left
    virtual_pin: 3
    physical_pin: 7
    servo_type: "300"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 2.61799
    servo_default_rad: 1.30900
    enabled: false

  - id: i2_left_cheek
    urdf_joint: i02_head_left_cheek_joint
    board: mega_left
    virtual_pin: 4
    physical_pin: 8
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_cheek
    urdf_joint: i02_head_right_cheek_joint
    board: mega_left
    virtual_pin: 5
    physical_pin: 9
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_upper_lip
    urdf_joint: i02_head_upper_lip_joint
    board: mega_left
    virtual_pin: 6
    physical_pin: 10
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_upper_left_eyelid
    urdf_joint: i02_head_left_top_eyelid_joint
    board: mega_left
    virtual_pin: 7
    physical_pin: 11
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_upper_right_eyelid
    urdf_joint: i02_head_right_top_eyelid_joint
    board: mega_left
    virtual_pin: 8
    physical_pin: 12
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_lower_left_eyelid
    urdf_joint: i02_head_left_bottom_eyelid_joint
    board: mega_left
    virtual_pin: 9
    physical_pin: 13
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_lower_right_eyelid
    urdf_joint: i02_head_right_bottom_eyelid_joint
    board: mega_left
    virtual_pin: 10
    physical_pin: 14
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_eye_horizontal
    urdf_joint: i02_head_left_eye_horizontal_joint
    board: mega_left
    virtual_pin: 11
    physical_pin: 15
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_eye_vertical
    urdf_joint: i02_head_left_eye_vertical_joint
    board: mega_left
    virtual_pin: 12
    physical_pin: 16
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_eye_horizontal
    urdf_joint: i02_head_right_eye_horizontal_joint
    board: mega_left
    virtual_pin: 13
    physical_pin: 17
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_eye_vertical
    urdf_joint: i02_head_right_eye_vertical_joint
    board: mega_left
    virtual_pin: 14
    physical_pin: 18
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_eyebrow
    urdf_joint: i02_head_left_eyebrow_joint
    board: mega_left
    virtual_pin: 15
    physical_pin: 19
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_eyebrow
    urdf_joint: i02_head_right_eyebrow_joint
    board: mega_left
    virtual_pin: 16
    physical_pin: 20
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_left_forehead
    urdf_joint: i02_head_left_forehead_joint
    board: mega_left
    virtual_pin: 17
    physical_pin: 21
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false

  - id: i2_right_forehead
    urdf_joint: i02_head_right_forehead_joint
    board: mega_left
    virtual_pin: 18
    physical_pin: 22
    servo_type: "180"
    offset_rad: 0.0
    direction: 1
    scale: 1.0
    servo_min_rad: 0.0
    servo_max_rad: 3.14159
    servo_default_rad: 1.57080
    enabled: false
```

