
# # extract_features.py folder/ output_file.csv

# output_file.csv

# song, feature1, feature2, ..., featurenN, genre

# Para cada cancion se obtienen 10 frames al azar.

import argparse
from os import listdir, makedirs
from os.path import isfile, join, exists, basename
import subprocess
import random


features = ['Energy', 'SpectralShapeStatistics', 'ZCR', 'SpectralRolloff', 'MagnitudeSpectrum']
block_size = 32768
step_size = 24576


def get_features(filename, feature_plan):
    output = '/tmp/extract_features_tmp/'
    subprocess.call(["yaafe.py", "-r", "44100", "-b", output, "-c", feature_plan])

    songname = basename(filename)

    num_frames = 0
    frames = []

    features = {"song": [filename]*10}

    for prefix in [feature_name[:3].lower() for feature_name in features]:
        csv_filename = join(output, songname + "." + feature_name[:3].lower() + ".csv")
        if num_frames == 0:
            process = subprocess.Popen(['wc', '-l', csv_filename], stdout=subprocess.PIPE)
            num_frames, err = process.communicate()
            print num_frames
            frames = random.sample(xrange(num_frames), 10)

        values = read_lines(csv_filename, frames)
        features[prefix] = values

    return features


def read_lines(filename, list_of_lines):
    # Leo usando sed para hacer lo mas rapido.
    args = ["sed", "-n"]
    for line in list_of_lines:
        args += ["-e", str(line) + "p"]
    args += [filename]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    lines, err = process.communicate()
    return lines.split('\n')


def save_feature_plan(directory):
    file_txt = ''
    for feature in features:
        file_txt += feature[:3].lower() + ': blockSize=' + str(block_size) + ' stepSize=' + str(step_size)

    filename = join(directory, 'feature_plan')
    f = open(filename, 'w')
    f.write(file_txt)
    return filename


def correct_type(filename):
    return filename.endswith('mp3') or filename.endswith('wav')


def get_list_of_files(input_directory):
    return [join(input_directory, f) for f in listdir(input_directory) if isfile(join(input_directory, f)) and correct_type(f)]


def save_features_csv(list_of_features):
    pass


def main():
    parser = argparse.ArgumentParser(description='Extrae los features de las canciones y los guarda en un csv.')
    parser.add_argument('-i', '--input', help='Directorio donde se encuentran las canciones', required=True)
    parser.add_argument('-o', '--output', help='Nombre de archivo donde escribir los features', required=True)
    args = vars(parser.parse_args())

    list_of_files = get_list_of_files(args['input'])
    list_of_features = []

    directory = '/tmp/extract_features_tmp'
    if not exists(directory):
        makedirs(directory)

    feature_plan = save_feature_plan(directory)

    for filename in list_of_files:
        features = get_features(filename, feature_plan)
        list_of_features += [features]

    save_features_csv(list_of_features)


if __name__ == '__main__':
    main()
