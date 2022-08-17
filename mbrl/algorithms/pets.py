# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Optional

import gym
import numpy as np
import omegaconf
import torch

import mbrl.constants
import mbrl.models
import mbrl.planning
import mbrl.types
import mbrl.util
import mbrl.util.common
import mbrl.util.math
from omegaconf import OmegaConf

EVAL_LOG_FORMAT = mbrl.constants.EVAL_LOG_FORMAT


def train(
    env: gym.Env,
    termination_fn: mbrl.types.TermFnType,
    reward_fn: mbrl.types.RewardFnType,
    cfg: omegaconf.DictConfig,
    silent: bool = False,
    work_dir: Optional[str] = None,
) -> np.float32:
    # print(dir(env))
    # ------------------- Initialization -------------------
    debug_mode = cfg.get("debug_mode", False)

    obs_shape = env.observation_space.shape
    act_shape = env.action_space.shape

    rng = np.random.default_rng(seed=cfg.seed)
    torch_generator = torch.Generator(device=cfg.device)
    if cfg.seed is not None:
        torch_generator.manual_seed(cfg.seed)

    work_dir = work_dir or os.getcwd()
    print(f"Results will be saved at {work_dir}.")

    if silent:
        logger = None
    else:
        logger = mbrl.util.Logger(work_dir,
        use_wandb=bool(cfg.get("use_wandb", 0)),
        wandb_name=cfg.experiment,
        wandb_project_name=cfg.wandb_project_name,
        wandb_config=OmegaConf.to_container(cfg, resolve=False),
        wandb_commit_interval_in_secs=cfg.overrides.get(
        "wandb_commit_interval_in_secs", 60)
        )
        logger.register_group(
            mbrl.constants.RESULTS_LOG_NAME, EVAL_LOG_FORMAT, color="green"
        )

    # -------- Create and populate initial env dataset --------
    dynamics_model = mbrl.util.common.create_one_dim_tr_model(cfg, obs_shape, act_shape)
    use_double_dtype = cfg.algorithm.get("normalize_double_precision", False)
    dtype = np.double if use_double_dtype else np.float32
    replay_buffer = mbrl.util.common.create_replay_buffer(
        cfg,
        obs_shape,
        act_shape,
        rng=rng,
        obs_type=dtype,
        action_type=dtype,
        reward_type=dtype,
    )
    print('POPULATING BUFFER')
    mbrl.util.common.rollout_agent_trajectories(
        env,
        # cfg.algorithm.initial_exploration_steps,
        len(env.manoeuvres),
        mbrl.planning.AcroAgent(env),
        # mbrl.planning.RandomAgent(env),
        {},
        replay_buffer=replay_buffer,
        collect_full_trajectories=True,
    )
    # env.set_(0)
    env.close()
    replay_buffer.save(work_dir)

    # ---------------------------------------------------------
    # ---------- Create model environment and agent -----------
    model_env = mbrl.models.ModelEnv(
        env, dynamics_model, termination_fn, reward_fn, generator=torch_generator
    )
    model_trainer = mbrl.models.ModelTrainer(
        dynamics_model,
        optim_lr=cfg.overrides.model_lr,
        weight_decay=cfg.overrides.model_wd,
        logger=logger,
    )

    agent = mbrl.planning.create_trajectory_optim_agent_for_model(
        model_env, cfg.algorithm.agent, num_particles=cfg.algorithm.num_particles
    )

    # ---------------------------------------------------------
    # --------------------- Training Loop ---------------------
    env_steps = 0
    first_loop = True
    current_trial = 0
    max_total_reward = -np.inf
    train_flag = True
    while env_steps < cfg.overrides.num_steps:
        # print(f'env_steps: {env_steps}')
        # print(f'ROLLOUT')
        reset_flag = True

        done = False
        total_reward = 0.0
        steps_trial = 0
        while not done:
            # --------------- Model Training -----------------
            if current_trial % cfg.algorithm.freq_train_model == 0 and train_flag == True:
                # env.close()
                print('TRAINING MODEL')
                mbrl.util.common.train_model_and_save_model_and_data(
                    dynamics_model,
                    model_trainer,
                    cfg.overrides,
                    replay_buffer,
                    work_dir=work_dir,
                )
                train_flag = False
                reset_flag = True
            if reset_flag:
                env.render()
                obs = env.reset()
                agent.reset()
                reset_flag = False
            # print('Doing rollout...')
            # --- Doing env step using the agent and adding to model dataset ---
            next_obs, reward, done, _ = mbrl.util.common.step_env_and_add_to_buffer(
                env, obs, agent, {}, replay_buffer
            )

            obs = next_obs
            total_reward += reward
            steps_trial += 1
            env_steps += 1

            if debug_mode:
                print(f"Step {env_steps}: Reward {reward:.3f}.")

        if logger is not None:
            logger.log_data(
                mbrl.constants.RESULTS_LOG_NAME,
                {"env_step": env_steps, "episode_reward": total_reward},
                commit=True
            )
        current_trial += 1
        train_flag = True
        env.close()
        if debug_mode:
            print(f"Trial: {current_trial }, reward: {total_reward}.")

        max_total_reward = max(max_total_reward, total_reward)

    return np.float32(max_total_reward)
