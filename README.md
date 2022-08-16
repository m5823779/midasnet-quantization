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

2) download download [ReDWeb_V1](https://sites.google.com/site/redwebcvpr18/) dataset for weight calibration

3) (option) for ReDWeb_V1 dataset run `python gen_val.py` to generate `ReDWeb_validation_360.txt` annotation file 

4) Pytorch to Onnx model
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
mo -m ./model/onnx/midasnet_v21.onnx -o ./model/openvino/ --input_shape [1,3,384,384] --layout [n,c,h,w] --reverse_input_channels 
mo -m ./model/onnx/midasnet_v21_small.onnx -o ./model/openvino/ --input_shape [1,3,256,256] --layout [n,c,h,w] --reverse_input_channels 
```

5) accuracy checker (Base line)
```buildoutcfg
accuracy_check -c midasnet_v21_ReDWeb.yml
accuracy_check -c midasnet_v21_small_ReDWeb.yml
```

6) Benchmark speed test
```buildoutcfg
benchmark_app -m ./model/openvino/midasnet_v21.xml
benchmark_app -m ./model/openvino/midasnet_v21_small.xml
```

7) Quantization
```buildoutcfg
pot --config midasnet_v21_ReDWeb.json --output-dir ./model/openvino --evaluate --log-level INFO
pot --config midasnet_v21_small_ReDWeb.json --output-dir ./model/openvino --evaluate --log-level INFO
```

8) Do step 6 with new quantize model

9) Test
```buildoutcfg
python run_openvino_cam.py -d CPU midasnet_v21_small.xml
```
`<path_to_python>\Lib\site-packages\openvino\tools\accuracy_checker\postprocessor` to find post processing



