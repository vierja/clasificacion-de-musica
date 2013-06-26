# -*- coding: utf-8 -*-
# # extract_features.py -i folder/ -o output_file.csv

# output_file.csv

# song, feature1, feature2, ..., featurenN

# Para cada cancion se obtienen 10 frames al azar.

import argparse
from os import listdir, makedirs
from os.path import isfile, join, exists
import subprocess
import random
import csv
from metadata_fetch import get_top_tag


features = ['Energy', 'SpectralShapeStatistics', 'ZCR', 'SpectralRolloff']
block_size = 32768
step_size = 24576
tmp_directory = '/tmp/extract_features_tmp'
num_frames_song = 10


def get_features(filename, feature_plan):
    process = subprocess.Popen(["python", "/usr/bin/yaafe.py", "-r", "44100", "-b", tmp_directory, "-c", feature_plan, filename], stdout=subprocess.PIPE)
    stdout, err = process.communicate()
    print err
    print stdout

    songname = filename

    num_frames = 0
    frames = []

    genre = get_top_tag(songname)

    features_list = {"song": [filename] * num_frames_song, "genre": genre}

    for prefix in [feature_name[-3:].lower() for feature_name in features]:
        csv_filename = join(tmp_directory, songname + "." + prefix + ".csv")
        if num_frames == 0:
            process = subprocess.Popen(['wc', '-l', csv_filename], stdout=subprocess.PIPE)
            num_frames, err = process.communicate()
            num_frames = num_frames.split(' ')[0]
            frames = random.sample(xrange(int(num_frames)), num_frames_song)

        values = read_lines(csv_filename, frames)
        features_list[prefix] = values

    return features_list


def read_lines(filename, list_of_lines):
    # Leo usando sed para hacer lo mas rapido.
    args = ["sed", "-n"]
    for line in list_of_lines:
        args += ["-e", str(line) + "p"]
    args += [filename]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    lines, err = process.communicate()
    return lines.split('\n')[:-1]  # Ultimo elemento es vacio.


def save_feature_plan(directory):
    file_txt = ''
    for feature in features:
        file_txt += feature[-3:].lower() + ': ' + feature + ' blockSize=' + str(block_size) + ' stepSize=' + str(step_size) + '\n'

    filename = join(directory, 'feature_plan')
    f = open(filename, 'w')
    f.write(file_txt)
    return filename


def correct_type(filename):
    return filename.endswith('mp3') or filename.endswith('wav')


def get_list_of_files(input_directory):
    return [join(input_directory, f) for f in listdir(input_directory) if isfile(join(input_directory, f)) and correct_type(f)]


def save_features_csv(list_of_map_features, output_file):
    print "Se guarda la lista de features en", output_file

    final_map = {}

    for feature_map in list_of_map_features:
        for feature in feature_map.keys():
            if feature in final_map:
                final_map[feature] += feature_map[feature]
            else:
                final_map[feature] = feature_map[feature]

    field_names = final_map.keys()

    list_of_lists = [final_map[field] for field in field_names]

    with open(output_file, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(field_names)
        writer.writerows(zip(*list_of_lists))


def main():
    parser = argparse.ArgumentParser(description='Extrae los features de las canciones y los guarda en un csv.')
    parser.add_argument('-i', '--input', help='Directorio donde se encuentran las canciones', required=True)
    parser.add_argument('-o', '--output', help='Nombre de archivo donde escribir los features', required=True)
    args = vars(parser.parse_args())

    list_of_files = get_list_of_files(args['input'])
    list_of_map_features = []

    if not exists(tmp_directory):
        makedirs(tmp_directory)

    feature_plan = save_feature_plan(tmp_directory)

    for filename in list_of_files:
        features = get_features(filename, feature_plan)
        list_of_map_features += [features]

    save_features_csv(list_of_map_features, args['output'])


if __name__ == '__main__':
    main()
