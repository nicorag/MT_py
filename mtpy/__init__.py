# -*- coding: utf-8 -*-
"""
==================
MTpy
==================

"""

__version__ = "1.1.5"

# load mtpy default logging config
from mtpy.utils.mtpy_logger import get_mtpy_logger

debug_logger = get_mtpy_logger(__name__, fn="mtpy_debug", level="debug")
debug_logger.debug("Starting MTpy Debug Log File")

error_logger = get_mtpy_logger("error", fn="mtpy_error", level="error")
matplotlib_logger = get_mtpy_logger(
    "matplotlib", fn="matplotlib_warn", level="warning"
)

# =============================================================================
# Commonly used objects
# =============================================================================
from mtpy.core.mt import MT
from mtpy.core.mt_collection import MTCollection

__all__ = ["MT", "MTCollection"]
