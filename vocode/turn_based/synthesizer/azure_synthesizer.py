from typing import Optional
from xml.etree import ElementTree
from pydub import AudioSegment
from vocode import getenv
import logging

from vocode.turn_based.synthesizer.base_synthesizer import BaseSynthesizer

DEFAULT_SAMPLING_RATE = 22050
DEFAULT_VOICE_NAME = "en-US-AriaNeural"
DEFAULT_PITCH = 0
DEFAULT_RATE = 15

NAMESPACES = {
    "mstts": "https://www.w3.org/2001/mstts",
    "": "https://www.w3.org/2001/10/synthesis",
}

ElementTree.register_namespace("", NAMESPACES[""])
ElementTree.register_namespace("mstts", NAMESPACES["mstts"])


class AzureSynthesizer(BaseSynthesizer):
    def __init__(
        self,
        sampling_rate: int = DEFAULT_SAMPLING_RATE,
        voice_name: str = DEFAULT_VOICE_NAME,
        pitch: int = DEFAULT_PITCH,
        rate: int = DEFAULT_RATE,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        import azure.cognitiveservices.speech as speechsdk

        self.speechsdk = speechsdk
        self.logger = logger or logging.getLogger(__name__)

        self.sampling_rate = sampling_rate
        speech_config = self.speechsdk.SpeechConfig(
            subscription=getenv("AZURE_SPEECH_KEY", api_key),
            region=getenv("AZURE_SPEECH_REGION", region),
        )
        # Logging the sampling rate
        self.logger.info(f"Setting sampling rate to {self.sampling_rate}")

        # Setting the output format based on the sampling rate
        output_format = {
            44100: self.speechsdk.SpeechSynthesisOutputFormat.Raw44100Hz16BitMonoPcm,
            48000: self.speechsdk.SpeechSynthesisOutputFormat.Raw48Khz16BitMonoPcm,
            24000: self.speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm,
            22050: self.speechsdk.SpeechSynthesisOutputFormat.Raw22050Hz16BitMonoPcm,
            16000: self.speechsdk.SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm,
            8000: self.speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm,
        }.get(self.sampling_rate)

        if output_format:
            speech_config.set_speech_synthesis_output_format(output_format)
        else:
            self.logger.error(f"Invalid sampling rate: {self.sampling_rate}")

        self.synthesizer = self.speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=None
        )
        self.voice_name = voice_name
        self.pitch = pitch
        self.rate = rate

    def create_ssml(self, message: str) -> str:
        ssml_root = ElementTree.fromstring(
            '<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US"></speak>'
        )
        voice = ElementTree.SubElement(ssml_root, "voice")
        voice.set("name", self.voice_name)
        voice_root = voice
        prosody = ElementTree.SubElement(voice_root, "prosody")
        prosody.set("pitch", f"{self.pitch}%")
        prosody.set("rate", f"{self.rate}%")
        prosody.text = message.strip()
        return ElementTree.tostring(ssml_root, encoding="unicode")

    def synthesize(self, text) -> AudioSegment:
        result = self.synthesizer.speak_ssml(self.create_ssml(text))
        if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
            self.logger.info("SynthesizingAudioCompleted result")
            return AudioSegment(
                result.audio_data,
                sample_width=2,
                frame_rate=self.sampling_rate,
                channels=1,
            )
        elif result.reason == self.speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            self.logger.warning(
                f"Speech synthesis canceled: {cancellation_details.reason}"
            )
            if cancellation_details.reason == self.speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    self.logger.error(
                        f"Error details: {cancellation_details.error_details}"
                    )
                    self.logger.error(
                        "Did you set the speech resource key and region values?"
                    )
        else:
            self.logger.error("Could not synthesize audio")
            raise Exception("Could not synthesize audio")
