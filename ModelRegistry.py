from tasks import save_audio_to_folder
from utils import convert_audio_bytes_to_wav
from ml_utils import create_model
class ModelRegistry:
    def __init__(self, user):
        # TODO
        super().__init__()
        self.user = user
        self.SAMPLES_PER_LABEL = 8
        self.MIN_CLASSES = 5


    def get_prediction_model(self, location):
        return None

    def get_all_models(self):
        # return { location -> model }
        return { }


    def get_audio_file_location(self, label, location):
        # Create corresponding folder if does not exist

        # Create corresponding audio folder
        pass


    def save_audio_file(self, audio_bytes, label, location):
        wav_file = convert_audio_bytes_to_wav(audio_bytes)

        file_location = get_audio_file_location(label, location)

        save_audio_to_folder(wav_file, file_location)


    def train_model(self, location):
        # Check if there is enough data for training
        if (can_train(location)):
            pass
        create_model

        

    


    def can_train(self, location):
        # Check the file system if there is the location

        # check if there is enough data in the locatino
        has_enough_training_data(location)
        pass


    def has_enough_training_data(self, location):
        # Check if the location has enough training data
        # Should be a recursive check for each label has enough audio data samples
        return True




    