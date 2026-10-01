#!/usr/bin/env python
"""Generate one-step forecast plots for pretrained property models."""

from enteric_emissions.config.settings import configure_logging
from enteric_emissions.pipelines.train import generate_plots_for_pretrained

if __name__ == "__main__":
    configure_logging()
    generate_plots_for_pretrained()
