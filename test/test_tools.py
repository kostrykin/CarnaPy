import pathlib
import matplotlib.pyplot as plt
import numpy as np

SOURCE_PATH = pathlib.Path('@CMAKE_CURRENT_SOURCE_DIR@')

class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def get_expected_rendering(name):
    expected_img_path = SOURCE_PATH / f'renderings/{name}.png'
    assert expected_img_path.is_file(), expected_img_path
    return expected_img_path

def assert_rendering(name, result, max_uint8_rms=0.5):
    try:
        expected_img_path = get_expected_rendering(name)
        expected_img = (plt.imread(expected_img_path)[:, :, :3] * 255).round().astype(np.uint8)
        assert result.shape == expected_img.shape, f'Expected shape {expected_img.shape} but found {result.shape}'
        assert result.dtype == expected_img.dtype, f'Expected dtype {expected_img.dtype} but dtype {result.dtype}'
        rms_error = np.sqrt(((expected_img - result) ** 2).mean())
        assert rms_error < max_uint8_rms, f'RMS error in 8bit representation: {rms_error}'
    except:
        output_path = f'/tmp/{name}.png'
        print(f'{Color.BOLD}{Color.RED}Test failed: {name}{Color.END}')
        print(f'{Color.BOLD}Result written to: {output_path}{Color.END}')
        plt.imsave(output_path, result)
        raise

