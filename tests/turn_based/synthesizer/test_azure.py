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

    # We are going to synthesize a text using the AzureSynthesizer instance
    # The text to be synthesized is defined as a string
    text_to_synthesize = "Hello, this is a test."

    # Create SSML from the text
    ssml_text = synthesizer.create_ssml(text_to_synthesize)

    # Call the speak_ssml method of the synthesizer instance
    # The result is a SpeechSynthesisResult instance
    result = synthesizer.synthesizer.speak_ssml(ssml_text)

    # Check if the synthesis was successful
    # Check if the synthesis was successful
    if result.reason == synthesizer.speechsdk.ResultReason.SynthesizingAudioCompleted:
        # If successful, convert the result to an AudioSegment instance
        audio_segment = AudioSegment(
            result.audio_data,
            sample_width=2,
            frame_rate=synthesizer.sampling_rate,
            channels=1,
        )
        # Now we can do something with the audio_segment, for example, save it to a file
        # We will use the export method of the AudioSegment instance
        # The export method requires a file name and a format
        # audio_segment.export("output.wav", format="wav")
    elif result.reason == synthesizer.speechsdk.ResultReason.Canceled:
        # If the synthesis was canceled, log the reason
        cancellation_details = result.cancellation_details
        synthesizer.logger.warning(
            f"Speech synthesis canceled: {cancellation_details.reason}"
        )
        if (
            cancellation_details.reason
            == synthesizer.speechsdk.CancellationReason.Error
        ):
            if cancellation_details.error_details:
                synthesizer.logger.error(
                    f"Error details: {cancellation_details.error_details}"
                )
                synthesizer.logger.error(
                    "Did you set the speech resource key and region values?"
                )
    else:
        # If the synthesis was not successful, log the reason
        synthesizer.logger.error("Could not synthesize audio")
