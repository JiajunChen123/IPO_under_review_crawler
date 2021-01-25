import pickle

def load_pickle(path_to_file):
    with open(path_to_file, 'rb') as file:
        data = pickle.load(file)
    return data


def save_pickle(obj, path_to_file):
    with open(path_to_file, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)