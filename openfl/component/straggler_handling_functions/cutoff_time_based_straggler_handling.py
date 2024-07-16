# Copyright (C) 2020-2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Cutoff time based Straggler Handling function."""
import numpy as np
import time
import threading
from typing import Callable
from logging import getLogger

from openfl.component.straggler_handling_functions import StragglerHandlingFunction


class CutoffTimeBasedStragglerHandling(StragglerHandlingFunction):
    def __init__(
        self,
        round_start_time=None,
        straggler_cutoff_time=np.inf,
        minimum_reporting=1,
        **kwargs
    ):
        if minimum_reporting == 0: raise ValueError("minimum_reporting cannot be 0")

        self.round_start_time = round_start_time
        self.straggler_cutoff_time = straggler_cutoff_time
        self.minimum_reporting = minimum_reporting
        self.is_timer_expired = False
        self.logger = getLogger(__name__)

        if self.straggler_cutoff_time == np.inf:
            self.logger.warning(
                "CutoffTimeBasedStragglerHandling is disabled as straggler_cutoff_time "
                "is set to np.inf."
            )

    def reset_policy_for_round(self) -> None:
        """
        Control whether to start the timer or not.
        """
        self.is_timer_expired = False

    def start_policy(
        self, callback: Callable, collaborator_name: str
    ) -> None:
        """
        Start time-based straggler handling policy for collaborator for
        a particular round.

        Args:
            callback: Callable
                Callback function for when straggler_cutoff_time elapses
            collaborator_name: str
                Name of the collaborator

        Returns:
            None
        """
        # If straggler_cutoff_time is set to infinite or
        # if the timer already expired for the current round do not start
        # the timer again until next round.
        if self.straggler_cutoff_time == np.inf or self.is_timer_expired:
            return
        self.round_start_time = time.time()
        if hasattr(self, "timer"):
            self.timer.cancel()
            delattr(self, "timer")
        self.timer = threading.Timer(
            self.straggler_cutoff_time, callback,
        )
        self.timer.daemon = True
        self.timer.start()

    def straggler_cutoff_check(self, num_collaborators_done, all_collaborators=None):
        """
        If minimum_reporting collaborators have reported results within
        straggler_cutoff_time, then return True otherwise False.
        """
        cutoff = self.__straggler_time_expired() and self.__minimum_collaborators_reported(
            num_collaborators_done)
        return cutoff

    def __straggler_time_expired(self):
        """
        Determines if straggler_cutoff_time is elapsed
        """
        return self.round_start_time is not None and (
            (time.time() - self.round_start_time) > self.straggler_cutoff_time)

    def __minimum_collaborators_reported(self, num_collaborators_done):
        """
        If minimum required collaborators have reported results, then return True
        otherwise False.
        """
        return num_collaborators_done >= self.minimum_reporting
