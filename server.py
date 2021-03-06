from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from keras.models import load_model
import tensorflow as tf
import numpy as np
from vggish_input import waveform_to_examples
import homesounds
from pathlib import Path
import time
import argparse
import wget
from helpers import dbFS

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# contexts
context = homesounds.everything
# use this to change context -- see homesounds.py
active_context = homesounds.everything

# thresholds
PREDICTION_THRES = 0.5  # confidence
DBLEVEL_THRES = -30  # dB

CHANNELS = 1
RATE = 16000
CHUNK = RATE
MICROPHONES_DESCRIPTION = []
FPS = 60.0

# ###########################
# # Download model, if it doesn't exist
# ###########################
# MODEL_URL = "https://www.dropbox.com/s/cq1d7uqg0l28211/example_model.hdf5?dl=1"
# MODEL_PATH = "models/example_model.hdf5"
# print("=====")
# print("2 / 2: Checking model... ")
# print("=====")
# model_filename = "models/example_model.hdf5"
# homesounds_model = Path(model_filename)
# if (not homesounds_model.is_file()):
#     print("Downloading example_model.hdf5 [867MB]: ")
#     wget.download(MODEL_URL, MODEL_PATH)

# ##############################
# # Load Deep Learning Model
# ##############################
# print("Using deep learning model: %s" % (model_filename))
# model = load_model(model_filename)
# graph = tf.get_default_graph()

# ##############################
# # Setup Audio Callback
# ##############################


def audio_samples(in_data, frame_count, time_info, status_flags):
    global graph
    np_wav = np.fromstring(in_data, dtype=np.int16) / \
        32768.0  # Convert to [-1.0, +1.0]
    # Compute RMS and convert to dB
    rms = np.sqrt(np.mean(np_wav**2))
    db = dbFS(rms)

    # Make predictions
    x = waveform_to_examples(np_wav, RATE)
    predictions = []
    with graph.as_default():
        if x.shape[0] != 0:
            x = x.reshape(len(x), 96, 64, 1)
            print('Reshape x successful', x.shape)
            pred = model.predict(x)
            predictions.append(pred)
        print('Prediction succeeded')
        for prediction in predictions:
            context_prediction = np.take(
                prediction[0], [homesounds.labels[x] for x in active_context])
            m = np.argmax(context_prediction)
            if (context_prediction[m] > PREDICTION_THRES and db > DBLEVEL_THRES):
                print("Prediction: %s (%0.2f)" % (
                    homesounds.to_human_labels[active_context[m]], context_prediction[m]))

    return (in_data, pyaudio.paContinue)


@socketio.on('audio_feature_data')
def handle_source(json_data):
    data = str(json_data['data'])
    data = data[1:-1]
    print('Data before transform to np', data)
    x = np.fromstring(data, dtype=np.float16, sep=',')
    print('data after to numpy', x)
    x = x.reshape(1, 96, 64, 1)
    print('Successfully reshape audio features', x.shape)
    print('Prediction: Knocking (50%)')
    socketio.emit('audio_label',
                  {
                      'label': 'Knocking',
                      'accuracy': '0.95'
                  })

    # with graph.as_default():
    # if x.shape[0] != 0:
    #     x = x.reshape(len(x), 96, 64, 1)
    #     print('Successfully reshape x', x)
    #     # pred = model.predict(x)
    #     # predictions.append(pred)

    # print('Prediction: Speech (50%)')
    # socket.emit('audio_label',
    #             {
    #                 'label': 'Unrecognized Sound',
    #                 'accuracy': '1.0'
    #             })

    # for prediction in predictions:
    #     context_prediction = np.take(
    #         prediction[0], [homesounds.labels[x] for x in active_context])
    #     m = np.argmax(context_prediction)
    #     print('Max prediction', str(
    #         homesounds.to_human_labels[active_context[m]]), str(context_prediction[m]))
    #     if (context_prediction[m] > PREDICTION_THRES and db > DBLEVEL_THRES):
    #         socketio.emit('audio_label',
    #                       {'label': str(homesounds.to_human_labels[active_context[m]]),
    #                        'accuracy': str(context_prediction[m])})
    #         print("Prediction: %s (%0.2f)" % (
    #             homesounds.to_human_labels[active_context[m]], context_prediction[m]))
    # socket.emit('audio_label',
    #             {
    #                 'label': 'Unrecognized Sound',
    #                 'accuracy': '1.0'
    #             })


@socketio.on('audio_data')
def handle_source(json_data):
    data = str(json_data['data'])
    data = data[1:-1]
    global graph
    np_wav = np.fromstring(data, dtype=np.int16, sep=',') / \
        32768.0  # Convert to [-1.0, +1.0]
    # Compute RMS and convert to dB
    print('Successfully convert to NP rep', np_wav)
    rms = np.sqrt(np.mean(np_wav**2))
    db = dbFS(rms)
    print('Db...', db)
    # Make predictions
    print('Making prediction...')
    x = waveform_to_examples(np_wav, RATE)
    predictions = []
    if x.shape[0] != 0:
        x = x.reshape(len(x), 96, 64, 1)
    print('Successfully reshape x', x.shape)
    # pred = model.predict(x)
    # predictions.append(pred)

    print('Prediction: Speech (50%)')
    socketio.emit('audio_label',
                  {
                      'label': 'Unrecognized Sound',
                      'accuracy': '1.0'
                  })
    # with graph.as_default():
    # if x.shape[0] != 0:
    #     x = x.reshape(len(x), 96, 64, 1)
    #     print('Successfully reshape x', x)
    #     # pred = model.predict(x)
    #     # predictions.append(pred)

    # print('Prediction: Speech (50%)')
    # socket.emit('audio_label',
    #             {
    #                 'label': 'Unrecognized Sound',
    #                 'accuracy': '1.0'
    #             })

    # for prediction in predictions:
    #     context_prediction = np.take(
    #         prediction[0], [homesounds.labels[x] for x in active_context])
    #     m = np.argmax(context_prediction)
    #     print('Max prediction', str(
    #         homesounds.to_human_labels[active_context[m]]), str(context_prediction[m]))
    #     if (context_prediction[m] > PREDICTION_THRES and db > DBLEVEL_THRES):
    #         socketio.emit('audio_label',
    #                       {'label': str(homesounds.to_human_labels[active_context[m]]),
    #                        'accuracy': str(context_prediction[m])})
    #         print("Prediction: %s (%0.2f)" % (
    #             homesounds.to_human_labels[active_context[m]], context_prediction[m]))
    # socket.emit('audio_label',
    #             {
    #                 'label': 'Unrecognized Sound',
    #                 'accuracy': '1.0'
    #             })


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


@app.route('/')
def index():
    return render_template('index.html',)


@socketio.on('send_message')
def handle_source(json_data):
    print('Receive message...' + str(json_data['message']))
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Server Says: ' + str(text)})
    print('Sending message back..')


""" TESTING SOCKET SERVER PART """
@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
