import tensorflow.compat.v2 as tf

from keras import backend
from keras.applications import imagenet_utils
from keras.engine import training
from keras.layers import VersionAwareLayers
from keras.utils import data_utils
from keras.utils import layer_utils

# isort: off
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.util.tf_export import keras_export

BASE_WEIGHT_PATH = (
    "https://storage.googleapis.com/tensorflow/keras-applications/mobilenet_v2/"
)
layers = None


def PDD_Model(
    input_shape=None,
    alpha=1.0,
    include_top=True,
    weights="imagenet",
    input_tensor=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
    **kwargs,
):
    global layers
    if "layers" in kwargs:
        layers = kwargs.pop("layers")
    else:
        layers = VersionAwareLayers()
    if kwargs:
        raise ValueError(f"Unknown argument(s): {kwargs}")
    if not (weights in {"imagenet", None} or tf.io.gfile.exists(weights)):
        raise ValueError(
            "The `weights` argument should be either "
            "`None` (random initialization), `imagenet` "
            "(pre-training on ImageNet), "
            "or the path to the weights file to be loaded.  "
            f"Received `weights={weights}`"
        )

    if weights == "imagenet" and include_top and classes != 1000:
        raise ValueError("classes should be 1000 when using `imagenet` " "weights")

    # Determine proper input shape and default size.
    # If both input_shape and input_tensor are used, they should match
    if input_shape is not None and input_tensor is not None:
        try:
            is_input_t_tensor = backend.is_keras_tensor(input_tensor)
        except ValueError:
            try:
                is_input_t_tensor = backend.is_keras_tensor(
                    layer_utils.get_source_inputs(input_tensor)
                )
            except ValueError:
                raise ValueError(
                    f"input_tensor: {input_tensor}"
                    "is not type input_tensor. "
                    f"Received `type(input_tensor)={type(input_tensor)}`"
                )
        if is_input_t_tensor:
            if backend.image_data_format() == "channels_first":
                if backend.int_shape(input_tensor)[1] != input_shape[1]:
                    raise ValueError(
                        "input_shape[1] must equal shape(input_tensor)[1] "
                        "when `image_data_format` is `channels_first`; "
                        "Received `input_tensor.shape="
                        f"{input_tensor.shape}`"
                        f", `input_shape={input_shape}`"
                    )
            else:
                if backend.int_shape(input_tensor)[2] != input_shape[1]:
                    raise ValueError(
                        "input_tensor.shape[2] must equal input_shape[1]; "
                        "Received `input_tensor.shape="
                        f"{input_tensor.shape}`, "
                        f"`input_shape={input_shape}`"
                    )
        else:
            raise ValueError(
                "input_tensor is not a Keras tensor; "
                f"Received `input_tensor={input_tensor}`"
            )

    # If input_shape is None, infer shape from input_tensor.
    if input_shape is None and input_tensor is not None:

        try:
            backend.is_keras_tensor(input_tensor)
        except ValueError:
            raise ValueError(
                "input_tensor must be a valid Keras tensor type; "
                f"Received {input_tensor} of type {type(input_tensor)}"
            )

        if input_shape is None and not backend.is_keras_tensor(input_tensor):
            default_size = 224
        elif input_shape is None and backend.is_keras_tensor(input_tensor):
            if backend.image_data_format() == "channels_first":
                rows = backend.int_shape(input_tensor)[2]
                cols = backend.int_shape(input_tensor)[3]
            else:
                rows = backend.int_shape(input_tensor)[1]
                cols = backend.int_shape(input_tensor)[2]

            if rows == cols and rows in [96, 128, 160, 192, 224]:
                default_size = rows
            else:
                default_size = 224

    # If input_shape is None and no input_tensor
    elif input_shape is None:
        default_size = 224

    # If input_shape is not None, assume default size.
    else:
        if backend.image_data_format() == "channels_first":
            rows = input_shape[1]
            cols = input_shape[2]
        else:
            rows = input_shape[0]
            cols = input_shape[1]

        if rows == cols and rows in [96, 128, 160, 192, 224]:
            default_size = rows
        else:
            default_size = 224

    input_shape = imagenet_utils.obtain_input_shape(
        input_shape,
        default_size=default_size,
        min_size=32,
        data_format=backend.image_data_format(),
        require_flatten=include_top,
        weights=weights,
    )

    if backend.image_data_format() == "channels_last":
        row_axis, col_axis = (0, 1)
    else:
        row_axis, col_axis = (1, 2)
    rows = input_shape[row_axis]
    cols = input_shape[col_axis]

    if weights == "imagenet":
        if alpha not in [0.35, 0.50, 0.75, 1.0, 1.3, 1.4]:
            raise ValueError(
                "If imagenet weights are being loaded, "
                "alpha must be one of `0.35`, `0.50`, `0.75`, "
                "`1.0`, `1.3` or `1.4` only;"
                f" Received `alpha={alpha}`"
            )

        if rows != cols or rows not in [96, 128, 160, 192, 224]:
            rows = 224
            logging.warning(
                "`input_shape` is undefined or non-square, "
                "or `rows` is not in [96, 128, 160, 192, 224]. "
                "Weights for input shape (224, 224) will be "
                "loaded as the default."
            )

    if input_tensor is None:
        img_input = layers.Input(shape=input_shape)
    else:
        if not backend.is_keras_tensor(input_tensor):
            img_input = layers.Input(tensor=input_tensor, shape=input_shape)
        else:
            img_input = input_tensor

    channel_axis = 1 if backend.image_data_format() == "channels_first" else -1

    first_block_filters = _make_divisible(32 * alpha, 8)
    x = layers.Conv2D(
        first_block_filters,
        kernel_size=3,
        strides=(2, 2),
        padding="same",
        use_bias=False,
        name="Conv1",
    )(img_input)
    x = layers.BatchNormalization(
        axis=channel_axis, epsilon=1e-3, momentum=0.999, name="bn_Conv1"
    )(x)
    x = layers.ReLU(6.0, name="Conv1_relu")(x)

    x = _inverted_res_block(
        x, filters=16, alpha=alpha, stride=1, expansion=1, block_id=0
    )

    x = _inverted_res_block(
        x, filters=24, alpha=alpha, stride=2, expansion=6, block_id=1
    )
    x = _inverted_res_block(
        x, filters=24, alpha=alpha, stride=1, expansion=6, block_id=2
    )

    x = _inverted_res_block(
        x, filters=32, alpha=alpha, stride=2, expansion=6, block_id=3
    )
    x = _inverted_res_block(
        x, filters=32, alpha=alpha, stride=1, expansion=6, block_id=4
    )
    x = _inverted_res_block(
        x, filters=32, alpha=alpha, stride=1, expansion=6, block_id=5
    )

    x = _inverted_res_block(
        x, filters=64, alpha=alpha, stride=2, expansion=6, block_id=6
    )
    x = _inverted_res_block(
        x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=7
    )
    x = _inverted_res_block(
        x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=8
    )
    x = _inverted_res_block(
        x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=9
    )

    x = _inverted_res_block(
        x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=10
    )
    x = _inverted_res_block(
        x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=11
    )
    x = _inverted_res_block(
        x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=12
    )

    x = _inverted_res_block(
        x, filters=160, alpha=alpha, stride=2, expansion=6, block_id=13
    )
    x = _inverted_res_block(
        x, filters=160, alpha=alpha, stride=1, expansion=6, block_id=14
    )
    x = _inverted_res_block(
        x, filters=160, alpha=alpha, stride=1, expansion=6, block_id=15
    )

    x = _inverted_res_block(
        x, filters=320, alpha=alpha, stride=1, expansion=6, block_id=16
    )

    # no alpha applied to last conv as stated in the paper:
    # if the width multiplier is greater than 1 we increase the number of output
    # channels.
    if alpha > 1.0:
        last_block_filters = _make_divisible(1280 * alpha, 8)
    else:
        last_block_filters = 1280

    x = layers.Conv2D(last_block_filters, kernel_size=1, use_bias=False, name="Conv_1")(
        x
    )
    x = layers.BatchNormalization(
        axis=channel_axis, epsilon=1e-3, momentum=0.999, name="Conv_1_bn"
    )(x)
    x = layers.ReLU(6.0, name="out_relu")(x)

    if include_top:
        x = layers.GlobalAveragePooling2D()(x)
        imagenet_utils.validate_activation(classifier_activation, weights)
        x = layers.Dense(classes, activation=classifier_activation, name="predictions")(
            x
        )

    else:
        if pooling == "avg":
            x = layers.GlobalAveragePooling2D()(x)
        elif pooling == "max":
            x = layers.GlobalMaxPooling2D()(x)

    # Ensure that the model takes into account any potential predecessors of
    # `input_tensor`.
    if input_tensor is not None:
        inputs = layer_utils.get_source_inputs(input_tensor)
    else:
        inputs = img_input

    # Create model.
    model = training.Model(inputs, x, name=f"mobilenetv2_{alpha:0.2f}_{rows}")

    # Load weights.
    if weights == "imagenet":
        if include_top:
            model_name = (
                "mobilenet_v2_weights_tf_dim_ordering_tf_kernels_"
                + str(float(alpha))
                + "_"
                + str(rows)
                + ".h5"
            )
            weight_path = BASE_WEIGHT_PATH + model_name
            weights_path = data_utils.get_file(
                model_name, weight_path, cache_subdir="models"
            )
        else:
            model_name = (
                "mobilenet_v2_weights_tf_dim_ordering_tf_kernels_"
                + str(float(alpha))
                + "_"
                + str(rows)
                + "_no_top"
                + ".h5"
            )
            weight_path = BASE_WEIGHT_PATH + model_name
            weights_path = data_utils.get_file(
                model_name, weight_path, cache_subdir="models"
            )
        model.load_weights(weights_path)
    elif weights is not None:
        model.load_weights(weights)

    return model


def _inverted_res_block(inputs, expansion, stride, alpha, filters, block_id):
    """Inverted ResNet block."""
    channel_axis = 1 if backend.image_data_format() == "channels_first" else -1

    in_channels = backend.int_shape(inputs)[channel_axis]
    pointwise_conv_filters = int(filters * alpha)
    # Ensure the number of filters on the last 1x1 convolution is divisible by
    # 8.
    pointwise_filters = _make_divisible(pointwise_conv_filters, 8)
    x = inputs
    prefix = f"block_{block_id}_"

    if block_id:
        # Expand with a pointwise 1x1 convolution.
        x = layers.Conv2D(
            expansion * in_channels,
            kernel_size=1,
            padding="same",
            use_bias=False,
            activation=None,
            name=prefix + "expand",
        )(x)
        x = layers.BatchNormalization(
            axis=channel_axis,
            epsilon=1e-3,
            momentum=0.999,
            name=prefix + "expand_BN",
        )(x)
        x = layers.ReLU(6.0, name=prefix + "expand_relu")(x)
    else:
        prefix = "expanded_conv_"

    # Depthwise 3x3 convolution.
    if stride == 2:
        x = layers.ZeroPadding2D(
            padding=imagenet_utils.correct_pad(x, 3), name=prefix + "pad"
        )(x)
    x = layers.DepthwiseConv2D(
        kernel_size=3,
        strides=stride,
        activation=None,
        use_bias=False,
        padding="same" if stride == 1 else "valid",
        name=prefix + "depthwise",
    )(x)
    x = layers.BatchNormalization(
        axis=channel_axis,
        epsilon=1e-3,
        momentum=0.999,
        name=prefix + "depthwise_BN",
    )(x)

    x = layers.ReLU(6.0, name=prefix + "depthwise_relu")(x)

    # Project with a pointwise 1x1 convolution.
    x = layers.Conv2D(
        pointwise_filters,
        kernel_size=1,
        padding="same",
        use_bias=False,
        activation=None,
        name=prefix + "project",
    )(x)
    x = layers.BatchNormalization(
        axis=channel_axis,
        epsilon=1e-3,
        momentum=0.999,
        name=prefix + "project_BN",
    )(x)

    if in_channels == pointwise_filters and stride == 1:
        return layers.Add(name=prefix + "add")([inputs, x])
    return x


def _make_divisible(v, divisor, min_value=None):
    if min_value is None:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v
