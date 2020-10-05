###############################################################################
# This program creates json files from the ecg data in the data set described
# in the README.md.
#
# wfdb package is required and available on pip.
# An output is a python dictionary, json_output with schema described below.
#
# json_output = {
#     'topic': ____
#     'record_Meta': {
#         'name': ____
#     },
#     'segment_meta': {
#         'index': ____
#         'index_neg': ____
#         'segment_start_time_s': ____
#     },
#     'signal_meta': {
#         'signal': ____
#         'window': ____
#         'frequency_Hz': ____
#         'unit': ____
#         'resolution_bit': ____
#         'check': ____
#     },
#     'subject_meta': {
#         'subject_number': ____
#         'subject_age': ____
#         'target_HR': ____
#     },
#     'signal': ____
# }
#
# DY200626
# DY201001
###############################################################################

import os
import csv
import json
import numpy as np
from scipy.signal import find_peaks
import wfdb

# to keep messages below about 10 kB
np.set_printoptions(threshold=3000)

data_dir = 'ecg-data/'

# Settings for getting and interpreting metadata
# Only two columns are interesting.
metadata_csv_path = 'ecg-data/subjects.csv'
subject_number_col_idx = 0
subject_age_col_idx = 5

output_dir = 'ecg/'
topic_header = 'ecg-'

max_target_HR = 220
target_sample_length = 15 * 60  # seconds
min_sample_length = 30  # seconds
channel_of_interest = 0


def main():
    topic_idx = 0
    max_signal_length = 0
    subjects = _get_measurements_info()
    
    for subject_number in subjects:
        
        if 'measurements' not in subjects[subject_number]:
            continue
        else:
            print(subject_number + ':')
        
        for measurement in subjects[subject_number]['measurements']:
            print('  ' + measurement)
            
            # record.p_signal is a numpy array
            record = wfdb.rdrecord(data_dir + measurement)
            record_signal_length = record.p_signal.shape[0]
            
            if record_signal_length < min_sample_length * record.fs:
                print('    ' + m + ' is too short, skipping..')
                continue
            
            record.subject_number = subject_number
            record.age = subjects[subject_number]['age']
            record.target_HR = max_target_HR - record.age
            record.peak_distance_threshold = \
                _calc_peak_distance_threshold(record, subjects)
            
            target_window_width = target_sample_length * record.fs
            record.num_windows = \
                np.round(record_signal_length / target_window_width)
            
            if record.num_windows == 0:
                record.num_windows = 1
                record.window_width = record_signal_length
            else:
                record.window_width = \
                    int(np.floor(target_window_width / record.num_windows))
                record.num_windows = int(record.num_windows)
            
            topic_idx, max_signal_length = \
                export_record(record, topic_idx, max_signal_length)
    
    print('Max Sample length is ' + str(max_signal_length) + ' elements')
    return


def export_record(record, topic_idx, max_signal_length):
    record_signal = record.p_signal[:, channel_of_interest]
    
    # each 15 min segment is a topic
    for window in range(record.num_windows):
        
        topic_idx += 1
        topic = topic_header + str(topic_idx).zfill(6)
        
        window_start = window * record.window_width
        window_end = (window + 1) * record.window_width
        signal = record_signal[window_start:window_end]
        
        prominence_threshold = _calc_prominence_threshold(signal, record)
        peaks, _ = find_peaks(signal, prominence=prominence_threshold
                              , distance=record.peak_distance_threshold)
        
        nPeaks = len(peaks)
        if nPeaks == 0:
            print('      No peak found in ' + m + ':'
                  + str(window).zfill(3) + ', skipping..')
            continue
        
        sample = signal[0:peaks[0]]
        _dump_record_to_json(topic, record, window, 0, -nPeaks - 1,
                             sample, 0)
        
        if len(sample) > max_signal_length:
            max_signal_length = len(sample)
        
        for p in range(nPeaks):
            idx = p + 1
            idx_neg = -(nPeaks + 1 - idx)
            
            if p < nPeaks - 1:
                sample = signal[peaks[p]:peaks[p + 1]]
            else:
                sample = signal[peaks[p]:]
            
            time_s = peaks[p] / record.fs
            _dump_record_to_json(topic, record, window, idx, idx_neg,
                                 sample, time_s)
            
            if len(sample) > max_signal_length:
                max_signal_length = len(sample)
    
    return topic_idx, max_signal_length


###############################################################################
# private utility functions
###############################################################################
def _calc_prominence_threshold(signal_segment, record):
    # calculate the prominence threshold for the signal_segment by windowing
    
    ptp_value = np.ptp(signal_segment)  # peak(+) to peak(-) range
    sub_window_width = 3 * record.fs  # 3 second window
    num_sub_window = np.round(len(signal_segment) / sub_window_width)
    sub_window_width = int(np.floor(len(signal_segment) / num_sub_window))
    num_sub_window = int(num_sub_window)
    
    for sw in range(num_sub_window):
        sub_signal_segment = \
            signal_segment[sw * sub_window_width: (sw + 1) * sub_window_width]
        ptp_seg = np.ptp(sub_signal_segment)
        if ptp_value > ptp_seg:
            ptp_value = ptp_seg
    
    prominence_threshold = 0.35 * ptp_value
    return prominence_threshold


def _calc_peak_distance_threshold(record, subjects):
    # record_name looks like "s0068-05022417"
    subject_number = record.record_name.split('-')[0].upper()  # "S0068"
    
    # peak_distance_threshold in length of array
    peak_distance_threshold = \
        60 * record.fs / (max_target_HR - subjects[subject_number]['age'])
    return peak_distance_threshold


def _get_measurements_info():
    # subjects_in_csv is a dictionary
    subjects_in_csv = _get_subjects_metadata()
    
    # get the dictionary of all measurements available.
    # all files with the same file name but different extensions
    # correspond to the same measurement
    
    subjects = dict()
    data_file_names = os.listdir(data_dir + '.')
    for fn in data_file_names:
        # '.dat' files are representatives
        ssp = fn.split('.')
        if ssp[1] != 'dat':
            continue
        
        # record_name looks like "s0068-05022417"
        record_name = ssp[0]
        subject_number = record_name.split('-')[0].upper()
        if subject_number not in subjects_in_csv:
            print('No metadata for ' + subject_number + ', '
                  + 'skipping: ' + record_name)
            continue
        
        if subject_number in subjects:
            subjects[subject_number]['measurements'].append(record_name)
        else:
            subjects[subject_number] = {
                'age': subjects_in_csv[subject_number]['age'],
                'measurements': [record_name]
            }
    
    return subjects


def _get_subjects_metadata():
    subjects = dict()
    with open(metadata_csv_path, 'r', encoding='utf8') as subjects_csv:
        reader = csv.reader(subjects_csv)
        _ = next(reader)  # ignore the first row
        
        for row in reader:
            subject_number = row[subject_number_col_idx]
            subject_age = row[subject_age_col_idx]
            
            if subject_number in subjects:
                print(subject_number + ': already have this subject')
                subjects[subject_number]['age'] = subject_age
            
            else:
                subjects[subject_number] = {}
                subjects[subject_number]['age'] = int(subject_age)
    
    return subjects


def _dump_record_to_json(topic, record, window, idx, idx_neg,
                         signal_segment, time_s):
    
    fmt = _format_switch(record.adc_res[channel_of_interest], 'g')
    
    signal_segment = np.array(signal_segment)
    signal_segment = np.array2string(
        signal_segment,
        max_line_width=float('inf'),
        suppress_small=False,
        formatter={'float_kind': lambda x: fmt % x}
    )
    
    json_path = output_dir + topic + '.json'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    json_output = {
        'topic': topic,
        'record_Meta': {
            'name': record.record_name
        },
        'segment_meta': {
            'index': idx,
            'index_neg': idx_neg,
            'segment_start_time_s': time_s
        },
        'signal_meta': {
            'signal': 'EKG',
            'window': window,
            'frequency_Hz': record.fs,
            'unit': record.units[channel_of_interest],
            'resolution_bit': record.adc_res[channel_of_interest],
            'check': record.checksum[channel_of_interest]
        },
        'subject_meta': {
            'subject_number': record.subject_number,
            'subject_age': record.age,
            'target_HR': record.target_HR
        },
        'signal': signal_segment
    }
    
    with open(json_path, 'a+') as outfile:
        json.dump(json_output, outfile)
        outfile.write('\n')


def _format_switch(bit_depth, fmt):
    switcher = {
        32: "%.16" + fmt,
        16: "%.8" + fmt,
        10: "%.5" + fmt,
        8: "%.4" + fmt
    }
    
    if bit_depth in switcher:
        return switcher[bit_depth]
    else:
        return "%.20" + fmt


if __name__ == '__main__':
    main()
