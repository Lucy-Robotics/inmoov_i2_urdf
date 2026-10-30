# Copyright 2025 Sentience Robotics Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
URDF_XACRO = ROOT / "description/robot_description/urdf/robot_description.urdf.xacro"


@pytest.mark.skipif(not URDF_XACRO.is_file(), reason="robot_description.urdf.xacro missing")
def test_production_urdf_has_no_unscaled_meshes():
    """Every <mesh scale> in the production xacro must use ${model_scale}."""
    text = URDF_XACRO.read_text(encoding="utf-8")
    assert 'scale="1.00000 1.00000 1.00000"' not in text, (
        "Found <mesh scale=\"1 1 1\"/> in robot_description.urdf.xacro: wrap mesh "
        "scale with ${model_scale}, otherwise joint frames shrink while DAEs stay full size."
    )


@pytest.mark.skipif(not URDF_XACRO.is_file(), reason="robot_description.urdf.xacro missing")
def test_production_urdf_has_no_raw_origin_xyz():
    """Every <origin xyz> in the production xacro must use ${model_scale}."""
    text = URDF_XACRO.read_text(encoding="utf-8")
    # Inertial COMs are SI values estimated for the current model_scale (see properties.xacro).
    text = re.sub(r"<inertial>.*?</inertial>", "", text, flags=re.S)
    raw = re.findall(r'<origin\b[^>]*\sxyz="([^"]+)"', text)
    offenders = [
        v for v in raw
        if v.strip()
        and "model_scale" not in v
        and not all(part.strip() in {"0", "0.0"} for part in v.split())
    ]
    assert not offenders, f"Unscaled origin xyz values found: {offenders[:5]}"
