import pathlib
import matplotlib.pyplot as plt
import numpy as np

SOURCE_PATH = pathlib.Path('@CMAKE_CURRENT_SOURCE_DIR@')

def get_expected_rendering(name):
    expected_img_path = SOURCE_PATH / f'renderings/{name}.png'
    assert expected_img_path.is_file(), expected_img_path
    return expected_img_path

def assert_rendering(name, result):
    try:
        expected_img_path = get_expected_rendering(name)
        expected_img = (plt.imread(expected_img_path)[:, :, :3] * 255).round().astype(np.uint8)
        assert result.shape == expected_img.shape, f'Expected shape {expected_img.shape} but found {result.shape}'
        assert result.dtype == expected_img.dtype, f'Expected dtype {expected_img.dtype} but dtype {result.dtype}'
        assert np.allclose(expected_img, result), np.linalg.norm(result - expected_img)
    except:
        output_path = f'/tmp/{name}.png'
        print(f'Test failed: {name}')
        print(f'Result written to: {output_path}')
        plt.imsave(output_path, result)
        raise

