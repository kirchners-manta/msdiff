"""
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

import pytest

from msdiff import calc_Hummer_correction


@pytest.mark.parametrize(
    "temperature, viscosity, box_length, delta_viscosity, k_hummer, delta_k_hummer",
    [
        (298.15, 0.00787, 1234, 0.00018, 63.80164586, 1.45924984),
        (350, 0.5, 10000, 0.0000, 0.14547387, 0.0000),
        (201, 0.00958, 5473, 0.00001, 7.96694943, 0.00831623),
    ],
)
def test_calc_Hummer_correction(
    temperature: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
    k_hummer: float,
    delta_k_hummer: float,
) -> None:
    assert calc_Hummer_correction(
        temperature, viscosity, box_length, delta_viscosity
    ) == pytest.approx((k_hummer, delta_k_hummer))


# @pytest.mark.parametrize(
#     "msd_file, mol_index, firststep, ndim, temp, viscosity, box_length, delta_viscosity, diff_coeff, delta_diff_coeff, r2, npoints_fit, k_hummer, delta_k_hummer",
#     [
#         (
#             pd.read_csv(
#                 Path(__file__).parent / "data" / "msd_ntf2.csv",
#                 sep=";",
#                 skiprows=1,
#                 names=["time", "msd_1", "derivative"],
#             ),
#             0,
#             661,
#             3,
#             298.15,
#             0.00787,
#             1234,
#             0.00018,
#             21.20593745,
#             0.00786019,
#             0.99995343,
#             341,
#             63.80164586,
#             1.45924984,
#         ),
#         (
#             pd.read_csv(
#                 Path(__file__).parent / "data" / "msd_emim.csv",
#                 sep=";",
#                 skiprows=1,
#                 names=["time", "msd_3", "derivative"],
#             ),
#             2,
#             71,
#             3,
#             350,
#             0.5,
#             10000,
#             0.0000,
#             192.81331505,
#             0.02890367,
#             0.9999790,
#             936,
#             None,
#             None,
#         ),
#     ],
# )
# def test_perform_linear_regression(
#     msd_file: pd.DataFrame,
#     mol_index: int,
#     firststep: int,
#     ndim: int,
#     temp: float,
#     viscosity: float,
#     box_length: float,
#     delta_viscosity: float,
#     diff_coeff: float,
#     delta_diff_coeff: float,
#     r2: float,
#     npoints_fit: int,
#     k_hummer: float | None,
#     delta_k_hummer: float | None,
# ) -> None:
#     assert get_diffusion_coefficient(
#         msd_file,
#         mol_index,
#         firststep,
#         ndim,
#         temp,
#         viscosity,
#         box_length,
#         delta_viscosity,
#     ) == pytest.approx(
#         (diff_coeff, delta_diff_coeff, r2, npoints_fit, k_hummer, delta_k_hummer)
#     )


# def test_fail_linear_regression() -> None:
#     msd_file = pd.DataFrame(
#         {
#             "time": [1, 2, 3, 4, 5],
#             "msd_1": [1, 2, 3, 4, 5],
#             "derivative": [1, 1, 1, 1, 1],
#         }
#     )
#     with pytest.raises(Warning):
#         get_diffusion_coefficient(msd_file, 0, 1, 3, 201, 0.007, 5000, 0.0001)

#     with pytest.raises(ValueError):
#         get_diffusion_coefficient(msd_file, 0, 4, 3, 201, 0.007, 5000, 0.0001)


# def test_neg_mol_index() -> None:
#     msd_file = pd.read_csv(
#         Path(__file__).parent / "data" / "msd_emim.csv",
#         sep=";",
#         skiprows=1,
#         names=["time", "msd_-3", "derivative"],
#     )
#     with pytest.raises(ValueError):
#         get_diffusion_coefficient(msd_file, -4, 300, 3, 201, 0.007, 5000, 0.0001)


# @pytest.mark.parametrize(
#     "cond_data, tskip, tol, firststep, laststep",
#     [
#         (
#             pd.DataFrame(
#                 {
#                     "time": np.arange(10, 10000, 10),
#                     "cond": np.arange(10, 10000, 10) ** 2,
#                 }
#             ),
#             0.1,
#             0.1,
#             -1,
#             -1,
#         )
#     ],
# )
# def test_no_cond_region(
#     cond_data: pd.DataFrame, tskip: float, tol: float, firststep: int, laststep: int
# ) -> None:
#     """Test if the linear region is found in the conductivity data."""

#     assert find_cond_region(cond_data, tskip, tol) == (firststep, laststep)


# # @pytest.mark.parametrize(
# #     "cond_data, firststep, laststep",
# #     [
# #         (
# #             pd.read_csv(
# #                 Path(__file__).parent / "data" / "conductivity_test_data.csv",
# #                 sep=";",
# #                 usecols=[0, 1],
# #                 names=["time", "cond"],
# #                 skiprows=1,
# #             ),
# #             3,
# #             100,
# #         )
# #     ],
# # )
# def test_cond_region_small() -> None:
#     """Test if the linear region in the conductivity data is small."""

#     cond_data = pd.read_csv(
#         Path(__file__).parent / "data" / "conductivity_test_data.csv",
#         sep=";",
#         usecols=[0, 1],
#         names=["time", "cond"],
#         skiprows=1,
#     )
#     with pytest.raises(Warning):
#         get_conductivity(cond_data, 10, 100)
#     with pytest.raises(ValueError):
#         get_conductivity(cond_data, 10, 10)
