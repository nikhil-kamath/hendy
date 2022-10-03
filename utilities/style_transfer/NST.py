import requests
from utilities.style_transfer.StyleContentModel import StyleContentModel
import time
import PIL.Image
import numpy as np
import os
import tensorflow as tf
import keras.utils

os.environ["TFHUB_MODEL_LOAD_FORMAT"] = 'COMPRESSED'



def style_transfer(target_link):
    dir_filepath = "./resources/neural/style/"
    content_image_name = "input_image.jpeg"
    style_image_name = "style_image.jpeg"
    test_image_name = "test_image.jpg"
    final_image_name = "final_image.jpg"
    
    style_path = tf.keras.utils.get_file(
        style_image_name, 'https://raw.githubusercontent.com/nikhil-kamath/neural-style-transfer/main/starry.jpeg')
    
    content_image = read_tensor_from_image_url(target_link)
    style_image = load_img(style_path)
    
    content_layers = ['block5_conv2']
    
    style_layers = ['block1_conv1',
                    'block2_conv1',
                    'block3_conv1',
                    'block4_conv1',
                    'block5_conv1']
    
    num_content_layers = len(content_layers)
    num_style_layers = len(style_layers)
    
    extractor = StyleContentModel(style_layers, content_layers)
    results = extractor(tf.constant(content_image))
    
    print("Styles:")
    overview(results["style"])
    print("Contents:")
    overview(results["content"])
    
    style_targets = extractor(style_image)['style']
    content_targets = extractor(content_image)['content']
    image = tf.Variable(content_image)
    
    optimizer = tf.optimizers.Adam(learning_rate=0.2, beta_1=0.99, epsilon=1e-1)
    style_weight = 1e-2
    content_weight = 1e4
    
    kwargs = {
        'style_targets': style_targets,
        'style_weight': style_weight, 
        'num_style_layers': num_style_layers,
        'content_targets': content_targets,
        'content_weight': content_weight,
        'num_content_layers': num_content_layers
    }
        
    train_step(image, extractor, optimizer, **kwargs)
    train_step(image, extractor, optimizer, **kwargs)
    train_step(image, extractor, optimizer, **kwargs)
    
    tensor_to_image(image).save(dir_filepath + test_image_name)
    
    start = time.time()
    
    epochs = 5
    steps_per_epoch = 100
    
    step = 0
    for _ in range(epochs):
        for _ in range(steps_per_epoch):
            step += 1
            train_step(image, extractor, optimizer, **kwargs)
            print(".", end="", flush=True)
        print(f"train step {step}")
    
    end = time.time()
    print("Total time: {:.1f}".format(end-start))
    
    tensor_to_image(image).save(dir_filepath + final_image_name)
    
    return dir_filepath + final_image_name
        

def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return PIL.Image.fromarray(tensor)


def load_img(path_to_img):
    max_dim = 512
    img = tf.io.read_file(path_to_img)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)

    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim

    new_shape = tf.cast(shape * scale, tf.int32)

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img

def overview(data):
    for name, output in sorted(data.items()):
        print("  ", name)
        print("    shape: ", output.numpy().shape)
        print("    min: ", output.numpy().min())
        print("    max: ", output.numpy().max())
        print("    mean: ", output.numpy().mean())
        print()

def clip_0_1(image):
    return tf.clip_by_value(image, clip_value_min=0., clip_value_max=1.)


def style_content_loss(outputs, style_targets, style_weight, num_style_layers, 
                       content_targets, content_weight, num_content_layers):
    style_outputs = outputs['style']
    content_outputs = outputs['content']
    style_loss = tf.add_n([tf.reduce_mean(
        (style_outputs[name]-style_targets[name])**2) for name in style_outputs.keys()])
    style_loss *= style_weight / num_style_layers

    content_loss = tf.add_n([tf.reduce_mean(
        (content_outputs[name]-content_targets[name])**2) for name in content_outputs.keys()])
    content_loss *= content_weight / num_content_layers
    return style_loss + content_loss

@tf.function()
def train_step(image, extractor, opt, **kwargs):
    with tf.GradientTape() as tape:
        outputs = extractor(image)
        loss = style_content_loss(outputs, **kwargs)

    grad = tape.gradient(loss, image)
    opt.apply_gradients([(grad, image)])
    image.assign(clip_0_1(image))


def read_tensor_from_image_url(url,
                               input_height=299,
                               input_width=299,
                               input_mean=0,
                               input_std=255):
    image_reader = tf.image.decode_jpeg(
        requests.get(url).content, channels=3, name="jpeg_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize(
        dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    return normalized
