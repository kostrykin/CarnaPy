import pathlib
import matplotlib.pyplot as plt
import numpy as np

SOURCE_PATH = pathlib.Path('@CMAKE_CURRENT_SOURCE_DIR@')

def get_expected_rendering(name):
    expected_img_path = SOURCE_PATH / f'renderings/{name}.png'
    assert expected_img_path.is_file()
    return expected_img_path

def assert_rendering(name, result):
    expected_img_path = get_expected_rendering(name)
    expected_img = (plt.imread(expected_img_path)[:, :, :3] * 255).round().astype(np.uint8)
    assert result.shape == expected_img.shape, f'Expected shape {expected_img.shape} but found {result.shape}'
    assert result.dtype == expected_img.dtype, f'Expected dtype {expected_img.dtype} but dtype {result.dtype}'
    assert np.allclose(expected_img, result), np.norm(result - expected_img)

