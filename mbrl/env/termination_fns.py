# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import torch
import math

# TODO remove act from all of these, it's not needed


def hopper(act: torch.Tensor, next_obs: torch.Tensor) -> torch.Tensor:
    assert len(next_obs.shape) == 2

    height = next_obs[:, 0]
    angle = next_obs[:, 1]
    not_done = (
        torch.isfinite(next_obs).all(-1)
        * (next_obs[:, 1:].abs() < 100).all(-1)
        * (height > 0.7)
        * (angle.abs() < 0.2)
    )

    done = ~not_done
    done = done[:, None]
    return done


def cartpole(act: torch.Tensor, next_obs: torch.Tensor) -> torch.Tensor:
    assert len(next_obs.shape) == 2

    x, theta = next_obs[:, 0], next_obs[:, 2]

    x_threshold = 2.4
    theta_threshold_radians = 12 * 2 * math.pi / 360
    not_done = (
        (x > -x_threshold)
        * (x < x_threshold)
        * (theta > -theta_threshold_radians)
        * (theta < theta_threshold_radians)
    )
    done = ~not_done
    print(not_done)
    print(done)
    done = done[:, None]
    print(done)
    return done


def inverted_pendulum(act: torch.Tensor, next_obs: torch.Tensor) -> torch.Tensor:
    assert len(next_obs.shape) == 2

    not_done = torch.isfinite(next_obs).all(-1) * (next_obs[:, 1].abs() <= 0.2)
    done = ~not_done

    done = done[:, None]

    return done


def no_termination(act: torch.Tensor, next_obs: torch.Tensor) -> torch.Tensor:
    assert len(next_obs.shape) == 2

    done = torch.Tensor([False]).repeat(len(next_obs)).bool().to(next_obs.device)
    done = done[:, None]
    return done


def walker2d(act: torch.Tensor, next_obs: torch.Tensor) -> torch.Tensor:
    assert len(next_obs.shape) == 2

    height = next_obs[:, 0]
    angle = next_obs[:, 1]
    not_done = (height > 0.8) * (height < 2.0) * (angle > -1.0) * (angle < 1.0)
    done = ~not_done
    done = done[:, None]
    return done


def ant(act: torch.Tensor, next_obs: torch.Tensor):
    assert len(next_obs.shape) == 2

    x = next_obs[:, 0]
    not_done = torch.isfinite(next_obs).all(-1) * (x >= 0.2) * (x <= 1.0)

    done = ~not_done
    done = done[:, None]
    return done


def humanoid(act: torch.Tensor, next_obs: torch.Tensor):
    assert len(next_obs.shape) == 2

    z = next_obs[:, 0]
    done = (z < 1.0) + (z > 2.0)

    done = done[:, None]
    return done

def realflight_hang(act: torch.Tensor, next_obs: torch.Tensor):
    assert len(next_obs.shape) == 2

    x = next_obs[:, 0].abs()
    y = next_obs[:, 1].abs()
    z = next_obs[:, 2]

    # print(x, y, z)
    not_done = (x < 5.0) * (y < 5.0) * (z > 5.0)
    # print(not_done)
    # print(done)
    done = ~not_done
    done = done[:, None]

    # print(done)

    return done

def perching_long(act: torch.Tensor, next_obs: torch.Tensor):
    # print(next_obs)
    assert len(next_obs.shape) == 2

    z = next_obs[0:, 1]
    # print(z)

    done = (z > 0)

    done = done[:, None]
    # print(done)
    return done

def realflight_level(act: torch.Tensor, next_obs: torch.Tensor):
    pass
