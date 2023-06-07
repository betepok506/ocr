import torch
import argparse
from src.model.model import OCR
from src.data.data import create_loaders, create_list_files
import torchvision.transforms as transforms
import pandas as pd
import json
import os
import hydra
from src.enities.prediction_pipeline_params import PredictingPipelineParams


@hydra.main(version_base=None, config_path='../configs', config_name='predict_config')
def predict_pipeline(params: PredictingPipelineParams):
    if params.create_annotations:
        create_list_files(params.path_to_data, params.path_to_annotations)
        # create_list_files("./data/test/test", params.path_to_annotations)
        print(f"Annotations created!")

    annotations = pd.read_csv(params.path_to_annotations)
    image_file_paths = annotations.iloc[:, 0].tolist()

    with open(os.path.join(params.path_to_info_for_model, "params.json"), "r") as infile:
        trainer_params = json.load(infile)

    trainer_params["ind2token"] = {int(k): v for k, v in trainer_params["ind2token"].items()}
    transform = transforms.Compose([
        transforms.ToPILImage(),
        # transforms.Grayscale(num_output_channels=1),
        # transforms.Resize((64, 224)),
        transforms.Resize(params.img_size),
        transforms.ToTensor()
    ])

    predict_loader = create_loaders(image_file_paths,
                                    transform=transform,
                                    split=False,
                                    batch_size=params.batch_size)

    device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
    print(f'Current device {device}')

    model = OCR(blank_token=trainer_params["blank_token"], blank_ind=trainer_params["blank_ind"],
                ind2token=trainer_params["ind2token"],
                token2ind=trainer_params["token2ind"], num_classes=trainer_params["num_classes"])
    model.to(device)

    print("Loading model")
    model.load(params.path_to_model)

    model.predict(predict_loader, params.output_dir)


# def get_args():
#     parser = argparse.ArgumentParser(description='Train the OCR on images and target text')
#     parser.add_argument('--epochs', '-e', metavar='E', type=int, default=10000, help='Number of epochs')
#     parser.add_argument('--path_to_data', type=str, default="./data/train/train", help='Path to folder with images')
#     parser.add_argument('--path_to_annotations', type=str, default="./data/list_images.csv",
#                         help='Path to annotations')
#     parser.add_argument('--batch-size', '-b', dest='batch_size', metavar='B', type=int, default=768, help='Batch size')
#     parser.add_argument('--load', '-f', type=str,
#                         default="./model/05-06-2023-10-33/checkpoints/Epoch_28_loss_1.87021.pt",
#                         help='Load model from a .pth file')
#     parser.add_argument('--output-dir', type=str, default="./model/05-06-2023-10-33",
#                         help='Load model from a .pth file')
#     parser.add_argument('--path-save', type=str, default="./results/result.csv", help='Load model from a .pth file')
#
#     return parser.parse_args()


if __name__ == "__main__":
    # args = get_args()
    # create_annotations(args.path_to_data, args.path_to_annotations)
    # fix_annotations(args.path_to_annotations, args.path_to_data, "./data/train/annotations.csv")
    # args.path_to_annotations = "./data/test_list.csv"
    predict_pipeline()