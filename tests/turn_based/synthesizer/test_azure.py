import sys
import pytest
from vocode.turn_based.synthesizer.azure_synthesizer import AzureSynthesizer
from pydub import AudioSegment
import logging


def test_synthesize():
    """
    Test the synthesize method of the AzureSynthesizer class.
    """
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Create an instance of AzureSynthesizer with the logger
    synthesizer = AzureSynthesizer(logger=logger)

    # Define a test text
    test_text = "Hello, world!"

    # Call the synthesize method and capture the output
    output = synthesizer.synthesize(test_text)

    # Assert that the output is an instance of AudioSegment
    assert isinstance(output, AudioSegment), "Output is not an instance of AudioSegment"

    # Assert that the output is not empty
    assert len(output) > 0, "Output is empty"
