import itertools
import os.path
import tempfile

import numpy as np
import openl3
import pytest
import requests
import soundfile as sf
from tqdm.auto import tqdm

import torchopenl3

AUDIO_URLS = [
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/chirp_1s.wav",
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/chirp_44k.wav",
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/chirp_mono.wav",
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/chirp_stereo.wav",
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/empty.wav",
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/short.wav",
"https://raw.githubusercontent.com/marl/openl3/master/tests/data/audio/silence.wav"
]

AUDIO_MODEL_PARAMS = {
    "content_type": ["env", "music"],
    "input_repr": ["linear", "mel128", "mel256"],
    "embedding_size": [512, 6144],
    "verbose": [0, 1],
    "center": [True, False],
    "hopsize": [0.1, 0.5],
}

class TestRegression:
    """
    Tests for any regressions against openl3.
    """

    def check_model_for_regression(self, modelparams, filenames):
        audios = []
        srs = []
        for filename in filenames:
            audio, sr = sf.read(filename)
            audios.append(audio)
            srs.append(sr)
        embeddings1, ts1 = openl3.get_audio_embedding(audios, srs, **modelparams)
        embeddings2, ts2 = openl3.get_audio_embedding(audios, srs, **modelparams)
        assert np.mean(np.abs(embeddings1 - embeddings2)) <= 1e-6
        assert np.mean(np.abs(ts1 - ts2)) <= 1e-6

    def test_regression(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            filenames = []
            for url in AUDIO_URLS:
                filename = os.path.join(tmpdirname, os.path.split(url)[1])
                print(filename)
                r = requests.get(url, allow_redirects=True)
                open(filename, 'wb').write(r.content)
            
            modelparamlist = [dict(zip(AUDIO_MODEL_PARAMS.keys(), p)) for p in itertools.product(*list(AUDIO_MODEL_PARAMS.values()))]
            for modelparams in tqdm(modelparamlist):
                self.check_model_for_regression(modelparams, filenames)
