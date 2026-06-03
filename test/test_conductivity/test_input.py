"""
Tests for conductivity input parsing.
"""

from __future__ import annotations

from pathlib import Path

from msdiff.conductivity.ionic_conductivity import read_input_conductivity


def test_read_input_conductivity_single_trajectory_two_species() -> None:
    data_file = (
        Path(__file__).parents[1] / "test_cli" / "data" / "conductivity_test_data.csv"
    )

    data = read_input_conductivity(str(data_file), uncert="none", species=2)

    assert list(data.columns) == [
        "time",
        "msd_1_self",
        "msd_2_self",
        "msd_1_cross",
        "msd_2_cross",
        "msd_1_2",
        "total_eh",
        "msd_1_self_std",
        "msd_1_cross_std",
        "msd_1_2_std",
        "msd_2_self_std",
        "msd_2_cross_std",
        "total_eh_std",
    ]
    assert (data.filter(like="_std") == 0.0).all().all()


def test_read_input_conductivity_std_three_species_trims_extra_columns(
    tmp_path: Path,
) -> None:
    data_file = tmp_path / "conductivity_avg.csv"
    data_file.write_text(
        "\n".join(
            [
                "# header",
                "1;10;0.1;20;0.2;30;0.3;40;0.4;50;0.5;60;0.6;70;0.7;80;0.8;90;0.9;100;1.0;999",
                "2;11;0.1;21;0.2;31;0.3;41;0.4;51;0.5;61;0.6;71;0.7;81;0.8;91;0.9;101;1.0;999",
                "3;12;0.1;22;0.2;32;0.3;42;0.4;52;0.5;62;0.6;72;0.7;82;0.8;92;0.9;102;1.0;999",
            ]
        ),
        encoding="utf8",
    )

    data = read_input_conductivity(str(data_file), uncert="std", species=3)

    assert data.shape == (2, 21)
    assert list(data.columns) == [
        "time",
        "msd_1_self",
        "msd_1_self_std",
        "msd_2_self",
        "msd_2_self_std",
        "msd_3_self",
        "msd_3_self_std",
        "msd_1_cross",
        "msd_1_cross_std",
        "msd_2_cross",
        "msd_2_cross_std",
        "msd_3_cross",
        "msd_3_cross_std",
        "msd_1_2",
        "msd_1_2_std",
        "msd_1_3",
        "msd_1_3_std",
        "msd_2_3",
        "msd_2_3_std",
        "total_eh",
        "total_eh_std",
    ]
    assert data.iloc[0, 0] == 2.0
    assert data.iloc[1, -1] == 1.0


def test_read_input_conductivity_variance_is_converted_to_std() -> None:
    data_file = (
        Path(__file__).parents[2]
        / "examples"
        / "conductivity"
        / "3_comp"
        / "conduct_3comp.csv"
    )

    data = read_input_conductivity(str(data_file), uncert="var", species=3)

    assert data.columns[0] == "time"
    assert data.loc[0, "msd_1_self_std"] == 0.001441**0.5
    assert data.loc[0, "msd_2_self_std"] == 0.000005**0.5
    assert data.loc[0, "msd_3_self_std"] == 0.011427**0.5
    assert data.loc[0, "msd_1_cross_std"] == 0.055585**0.5
    assert data.loc[0, "msd_1_2_std"] == 0.007359**0.5
    assert data.loc[0, "total_eh_std"] == 0.425035**0.5
