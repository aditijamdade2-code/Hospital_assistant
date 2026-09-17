import os
import pytest

# Ensure unit test suite always runs reliably with mock provider
os.environ["LLM_PROVIDER"] = "mock"
