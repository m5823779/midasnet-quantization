# Midasnet OpenVINO Quantization

[MidasNet](https://github.com/isl-org/MiDaS) is a model for monocular depth estimation trained by mixing several datasets;
as described in the following paper:
[Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-Shot Cross-Dataset Transfer](https://arxiv.org/abs/1907.01341)

"MiDaS v2.1 large" input is a blob that consists of a single image of `1, 3, 384, 384` in `RGB` order.

"MiDaS v2.1 small" input is a blob that consists of a single image of `1, 3, 256, 256` in `RGB` order.

The model output is an inverse depth map that is defined up to an unknown scale factor.

## Installation Dependencies:

* OpenVINO 2022.1.0
```buildoutcfg
pip install openvino-dev==2022.1.0
```

## Usage:

1) download model (MiDaS v2.1 large & MiDaS v2.1 small)
```buildoutcfg
wget https://github.com/isl-org/MiDaS/releases/download/v2_1/model-f6b98070.pt -O model/pytorch/midasnet_v21.pt
wget https://github.com/isl-org/MiDaS/releases/download/v2_1/model-small-70d6b9c8.pt -O model/pytorch/midasnet_v21_small.pt
```

2) download 2012 ImageNet validation dataset
```buildoutcfg
wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar
```

3) Pytorch to Onnx model
```buildoutcfg
python pytorch_to_onnx.py --model-name=MidasNet --model-path=./ --weights=./model/pytorch/midasnet_v21.pt --import-module=midas.midas_net --input-shape=1,3,384,384 --output-file=./model/onnx/midasnet_v21.onnx --input-names=image --output-names=inverse_depth --opset_version 11
python pytorch_to_onnx.py --model-name=MidasNet_small --model-path=./ --weights=./model/pytorch/midasnet_v21_small.pt --import-module=midas.midas_net_custom --input-shape=1,3,256,256 --output-file=./model/onnx/midasnet_v21_small.onnx --input-names=image --output-names=inverse_depth --opset_version 11
```

or download onnx directly
```buildoutcfg
wget https://github.com/isl-org/MiDaS/releases/download/v2_1/model-f6b98070.onnx -O model/onnx/midasnet_v21.onnx
wget https://github.com/isl-org/MiDaS/releases/download/v2_1/model-small.onnx -O model/onnx/midasnet_v21_small.onnx
```

4) Onnx to OpenVINO IR model
```buildoutcfg
mo -m ./model/onnx/midasnet_v21.onnx -o ./model/openvino/
mo -m ./model/onnx/midasnet_v21_small.onnx -o ./model/openvino/
```

5) accuracy checker (Base line)
```buildoutcfg
accuracy_check -c midasnet_v21.yml
accuracy_check -c midasnet_v21_small.yml
```

6) Quantization
```buildoutcfg
pot --config midasnet_v21.json --output-dir ./model/openvino
pot --config midasnet_v21_small.json --output-dir ./model/openvino
```

7) Test
```buildoutcfg
python run_openvino_cam.py -d CPU midasnet_v21_small.xml
```



