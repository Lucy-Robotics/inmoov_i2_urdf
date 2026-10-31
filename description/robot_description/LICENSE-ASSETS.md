# Model assets license — CC BY-NC 4.0

The robot model assets in this package are **not** covered by the GPL-3.0
`LICENSE` next to this file. They are derived from the InMoov robot and are
licensed under the
[Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/)
license (CC BY-NC 4.0). **Commercial use is not permitted.**

Covered files:

- `meshes/` — all visual (`.obj`/`.mtl`) and collision (`.stl`) meshes

Everything else in the package (`description/**/*.xacro`, `launch/`,
`config/`, `CMakeLists.txt`, `package.xml`) is GPL-3.0, see the `LICENSE`
at the package root.

## Attribution

- **Original design:** InMoov by Gaël Langevin — <https://inmoov.fr>.
  InMoov parts are published under a Creative Commons
  Attribution-NonCommercial license.
- **Intermediate source:**
  [Lucy-Robotics/inmoov_urdf](https://github.com/Lucy-Robotics/inmoov_urdf),
  which redistributes the InMoov-derived meshes (including the stand mesh)
  under CC BY-NC 4.0.
- **This adaptation:** Artur Fedjukevits — [Artur-Fedjukevits/inmoov_ros2](https://github.com/Artur-Fedjukevits/inmoov_ros2/tree/main/src/inmoov_description).

## Changes made

The meshes were reworked in Blender and are not identical to the original
InMoov parts:

- parts reassembled per URDF link and re-exported with LinkForge (OBJ, split
  into sub-meshes per link);
- InMoov i2 head / face parts added;
- some visual meshes decimated (jaw, head);
- collision geometry added: simplified STL meshes for the forearms,
  lower torso and thumbs, and primitive boxes/cylinders elsewhere;
- joint origins, axes and limits adjusted to the physical robot.
