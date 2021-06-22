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

def fail_test(name, *results, suffix=''):
    if isinstance(suffix, str) and len(suffix) > 0: suffix = f' ({suffix})'
    print(f'{Color.BOLD}{Color.RED}Test failed: {name}{Color.END}{suffix}')
    if len(results) == 0: return
    if len(results) == 1: results = (results[0], '')
    for result_idx in range(len(results) // 2):
        result, suffix = results[2 * result_idx], results[2 * result_idx + 1]
        output_path = f'/tmp/{name}{suffix}.png'
        print(f'{Color.BOLD}Result written to: {output_path}{Color.END}')
        plt.imsave(output_path, result)

def pass_test(name, suffix=''):
    if isinstance(suffix, str) and len(suffix) > 0: suffix = f' ({suffix})'
    print(f'{Color.BOLD}{Color.GREEN}Test passed: {name}{Color.END}{suffix}')

class BatchTest:
    def __init__(self):
        self.success = True

    def assert_true(self, statement, hint):
        if not self.update(statement): fail_test(hint)
        else: pass_test(hint)
        return statement

    def assert_allclose(self, expected, actual, hint):
        if not self.assert_true(np.allclose(expected, actual), hint):
            print('====== Expected: ======')
            print(expected)
            print('======= Actual: =======')
            print(actual)
            print('=======================')

    def update(self, value):
        self.success = self.success and value
        return value

    def finish(self):
        assert self.success, 'Batch test failed'

def assert_rendering(name, result, max_abs_error=50/255, max_rms_error=1e-3, defer=False, batch=None):
    if batch is not None: defer = True
    try:
        expected_img_path = get_expected_rendering(name)
        expected_img = plt.imread(expected_img_path)[:, :, :3]
        assert result.shape == expected_img.shape, f'Expected shape {expected_img.shape} but found {result.shape}'
        assert result.dtype == np.uint8, f'Expected dtype {np.uint8} but dtype {result.dtype}'
        result_f = result / 255
        abs_error = np.abs(expected_img - result_f).max()
        rms_error = np.sqrt(((expected_img - result_f) ** 2).mean())
        hint = f'Abs error: {abs_error:g}, RMS error: {rms_error:g}'
        assert abs_error <= max_abs_error and rms_error <= max_rms_error, hint
        pass_test(name, hint)
        return True
    except Exception as ex:
        fail_test(name, result, suffix=str(ex))
        if not defer: raise
        if batch is not None: batch.update(False)
        return False

