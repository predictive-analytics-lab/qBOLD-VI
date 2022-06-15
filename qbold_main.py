import numpy as np
import argparse
import tensorflow as tf
import wandb
from qbold_train_model import ModelTrainer


def setup_argparser(defaults_dict):
    parser = argparse.ArgumentParser(description='Train neural network for parameter estimation')

    parser.add_argument('-f', default='synthetic_data.npz', help='path to synthetic data file')
    parser.add_argument('-d', default='/its/home/km675/qbold', help='path to the real data directory')
    parser.add_argument('--no_units', type=int, default=defaults_dict['no_units'])
    parser.add_argument('--no_pt_epochs', type=int, default=defaults_dict['no_pt_epochs'])
    parser.add_argument('--no_ft_epochs', type=int, default=defaults_dict['no_ft_epochs'])
    parser.add_argument('--student_t_df', type=int, default=defaults_dict['student_t_df'])
    parser.add_argument('--crop_size', type=int, default=defaults_dict['crop_size'])
    parser.add_argument('--no_intermediate_layers', type=int, default=defaults_dict['no_intermediate_layers'])
    parser.add_argument('--kl_weight', type=float, default=defaults_dict['kl_weight'])
    parser.add_argument('--smoothness_weight', type=float, default=defaults_dict['smoothness_weight'])
    parser.add_argument('--pt_lr', type=float, default=defaults_dict['pt_lr'])
    parser.add_argument('--ft_lr', type=float, default=defaults_dict['ft_lr'])
    parser.add_argument('--dropout_rate', type=float, default=defaults_dict['dropout_rate'])
    parser.add_argument('--im_loss_sigma', type=float, default=defaults_dict['im_loss_sigma'])
    parser.add_argument('--use_layer_norm', type=bool, default=defaults_dict['use_layer_norm'])
    parser.add_argument('--use_r2p_loss', type=bool, default=defaults_dict['use_r2p_loss'])
    parser.add_argument('--multi_image_normalisation', type=bool, default=defaults_dict['multi_image_normalisation'])
    parser.add_argument('--activation', default=defaults_dict['activation'])
    parser.add_argument('--misalign_prob', type=float, default=defaults_dict['misalign_prob'])
    parser.add_argument('--use_blood', type=bool, default=defaults_dict['use_blood'])
    parser.add_argument('--channelwise_gating', type=bool, default=defaults_dict['channelwise_gating'])
    parser.add_argument('--full_model', type=bool, default=defaults_dict['full_model'])
    parser.add_argument('--save_directory', default=None)
    parser.add_argument('--use_population_prior', type=bool, default=defaults_dict['use_population_prior'])
    parser.add_argument('--inv_gamma_alpha', type=float, default=defaults_dict['inv_gamma_alpha'])
    parser.add_argument('--inv_gamma_beta', type=float, default=defaults_dict['inv_gamma_beta'])
    parser.add_argument('--gate_offset', type=float, default=defaults_dict['gate_offset'])
    parser.add_argument('--resid_init_std', type=float, default=defaults_dict['resid_init_std'])
    parser.add_argument('--use_wandb', type=bool, default=defaults_dict['use_wandb'])
    parser.add_argument('--infer_inv_gamma', type=bool, default=defaults_dict['infer_inv_gamma'])
    parser.add_argument('--use_mvg', type=bool, default=defaults_dict['use_mvg'])
    parser.add_argument('--uniform_prop', type=float, default=defaults_dict['uniform_prop'])
    parser.add_argument('--use_swa', type=bool, default=defaults_dict['use_swa'])
    parser.add_argument('--adamw_decay', type=float, default=defaults_dict['adamw_decay'])
    parser.add_argument('--pt_adamw_decay', type=float, default=defaults_dict['pt_adamw_decay'])
    parser.add_argument('--predict_log_data', type=bool, default=defaults_dict['predict_log_data'])

    return parser


def get_defaults():
    defaults = dict(
        no_units=30,
        no_intermediate_layers=1,
        student_t_df=2,  # Switching to None will use a Gaussian error distribution
        pt_lr=5e-5,
        ft_lr=5e-3,
        kl_weight=1.0,
        smoothness_weight=1.0,
        dropout_rate=0.0,
        no_pt_epochs=5,
        no_ft_epochs=40,
        im_loss_sigma=0.08,
        crop_size=16,
        use_layer_norm=False,
        activation='relu',
        use_r2p_loss=False,
        multi_image_normalisation=True,
        full_model=True,
        use_blood=True,
        misalign_prob=0.0,
        use_population_prior=True,
        use_wandb=True,
        inv_gamma_alpha=0.0,
        inv_gamma_beta=0.0,
        gate_offset=0.0,
        resid_init_std=1e-1,
        channelwise_gating=True,
        infer_inv_gamma=False,
        use_mvg=False,
        uniform_prop=0.1,
        use_swa=True,
        adamw_decay=2e-4,
        pt_adamw_decay=2e-4,
        predict_log_data=True
    )
    return defaults




if __name__ == '__main__':
    import sys
    import yaml

    tf.random.set_seed(1)
    np.random.seed(1)

    yaml_file = None
    # If we have a single argument and it's a yaml file, read the config from there
    if (len(sys.argv) == 2) and (".yaml" in sys.argv[1]):
        # Read the yaml filename
        yaml_file = sys.argv[1]
        # Remove it from the input arguments to also allow the default argparser
        sys.argv = [sys.argv[0]]

    cmd_parser = setup_argparser(get_defaults())
    args = cmd_parser.parse_args()
    args = vars(args)

    if yaml_file is not None:
        opt = yaml.load(open(yaml_file), Loader=yaml.FullLoader)
        # Overwrite defaults with yaml config, making sure we use the correct types
        for key, val in opt.items():
            if args.get(key):
                args[key] = type(args.get(key))(val)
            else:
                args[key] = val

    if args['use_wandb']:
        wandb.init(project='qbold_inference', entity='kasiamoj')
        if not args.get('name') is None:
            wandb.run.name = args['name']

        wandb.config.update(args)
        model_trainer = ModelTrainer(wandb.config)
        model_trainer.build_model()
        model_trainer.train_model()

    else:
        model_trainer = ModelTrainer(args)
        model_trainer.build_model()
        model_trainer.train_model()
