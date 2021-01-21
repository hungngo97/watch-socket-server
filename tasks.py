# TODO: Create a celery task to save audio to a file location
from ml_utils import create_model
def save_audio_to_folder(audio_file, file_location):
    pass


def create_model(folder_path, output_model_name, output_location):
    # TODO: Start training here
    model = create_model
    save_model(model, output_location + '/model')
    # Need to notify user once the model training is done
    pass


def save_model(model, model_location):
    pass

