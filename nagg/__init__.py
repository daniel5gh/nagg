# coding=utf-8
__author__ = 'daniel'

import base64
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, np.ndarray):
            # noinspection PyUnresolvedReferences
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            # we need this to be a string, not bytes
            data_b64 = data_b64.decode('ascii')
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return super().default(obj)


def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    :type dct: dict
    :param dct: json encoded ndarray
    :rtype: np.ndarray
    :return: new np.ndarray if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct


class NumpyDecoder(json.JSONDecoder):
    def __init__(self, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True,
                 object_pairs_hook=None):
        object_hook = json_numpy_obj_hook
        super().__init__(object_hook, parse_float, parse_int, parse_constant, strict, object_pairs_hook)


def json_numpy_loads(data):
    print('data', data)
    return json.loads(data, cls=NumpyDecoder)


def test():
    expected = np.arange(100, dtype=np.float)
    dumped = json.dumps(expected, cls=NumpyEncoder)
    result = json.loads(dumped, cls=NumpyDecoder)

    # print(expected)
    # print(dumped)
    # print(result)
    # print(len(dumped))

    # None of the following assertions will be broken.
    assert result.dtype == expected.dtype, "Wrong Type"
    assert result.shape == expected.shape, "Wrong Shape"
    assert np.allclose(expected, result), "Wrong Values"

    key = 'level1'
    expected2 = {key: expected}
    dumped2 = json.dumps(expected2, cls=NumpyEncoder)
    result2 = json_numpy_loads(dumped2)

    assert result2[key].dtype == expected2[key].dtype, "Wrong Type"
    assert result2[key].shape == expected2[key].shape, "Wrong Shape"
    assert np.allclose(expected2[key], result2[key]), "Wrong Values"
    print(result2)

if __name__ == '__main__':
    test()
