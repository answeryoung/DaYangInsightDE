import os
import sys
import csv
import json
import numpy as np

from scipy.signal import find_peaks
import wfdb


data_dir = 'ecg-data/'
subject_meta_path = 'ecg-data/subjects.csv'

output_json_name = 'ecg-data-g.json'

targetHR = 220;
sample_length     = 15*60; # seconds, target sample length
min_sample_lenght = 30; # seconds
channel_of_interest = 0;

subject_number_col_idx = 0
subject_age_col_idx    = 5

# max_signal_length = 0
# topic_idx = 0
# subjects  = get_measurements_info(data_dir)
def main():
    topic_idx = 0
    max_signal_length = 0
    subjects  = get_measurements_info(data_dir)
    for s in subjects:
        if 'measurements' not in subjects[s]:
            continue
        else:
            print(s+':')

        for m in subjects[s]['measurements']:
            print('  '+ m)
            record       = wfdb.rdrecord(data_dir+m)
            signal_whole = record.p_signal[:,channel_of_interest]
#            record.fs    = int(record.fs/2)
            if len(signal_whole) < min_sample_lenght*record.fs:
                print('    '+ m +' is too short, skipping..')
                continue

            peak_distance_thd = set_peak_distance_thd(record, subjects)

            window_width = sample_length*record.fs
            nWindow      = np.round(len(signal_whole)/window_width)
            if nWindow == 0:
                nWindow = 1
                window_width = len(signal_whole)
            else:
                window_width = int(np.floor(len(signal_whole)/nWindow))
                nWindow      = int(nWindow)

            for w in range(nWindow):
                topic      = mk_topic(topic_idx) # each 15 min segment is a topic
                topic_idx += 1

                signal          = signal_whole[(w*window_width):((w+1)*window_width)]
                prominence_thd  = set_prominence_thd(signal, record)
                peaks, _        = find_peaks( signal, prominence=prominence_thd
                                              , distance=peak_distance_thd)

                nPeaks = len(peaks)
                if nPeaks == 0:
                    print('      No peak found in '+ m +':'+str(w).zfill(3)+', skipping..')
                    continue

                sample = signal[0:peaks[0]]
                dump_to_json( output_json_name, topic, record, w
                            , subjects, 0, -nPeaks-1, sample, 0)
                if len(sample) > max_signal_length:
                    max_signal_length = len(sample);
                for p in range(nPeaks):
                    idx     = p + 1
                    idx_neg = -(nPeaks+1 - idx)
                    if p < nPeaks - 1:
                        sample = signal[peaks[p]:peaks[p+1]]
                    else:
                        sample = signal[peaks[p]:-1]
                    time_s = peaks[p]/record.fs
                    dump_to_json( output_json_name, topic, record, w
                                , subjects, idx, idx_neg, sample, time_s)
                    if len(sample) > max_signal_length:
                        max_signal_length = len(sample)
    print('Max Sample length is '+str(max_signal_length)+' elements')
    return

#######################################################################
#
# Utility functions
#######################################################################
def mk_topic(idx):
    topic = 'ecg-'+str(idx).zfill(6)
    print(topic)
    return topic




def set_prominence_thd(signal_segment, record):
    ptp_value       = np.ptp(signal_segment)
    subwindow_width = 3*record.fs # 3 second window
    nSubwindow      = np.round(len(signal_segment)/subwindow_width)
    subwindow_width = int(np.floor(len(signal_segment)/nSubwindow))
    nSubwindow      = int(nSubwindow)
    for sw in range(nSubwindow):
        subsignal = signal_segment[sw*subwindow_width:(sw+1)*subwindow_width]
        ptp_seg   = np.ptp(subsignal)
        if ptp_value > ptp_seg:
            ptp_value = ptp_seg
    prominence_thd = 0.35*ptp_value

    return prominence_thd


def set_peak_distance_thd(record, subjects):
    subject_number = record.record_name.split('-')[0].upper()
    peak_distance_thd = 60*record.fs/(targetHR - subjects[subject_number]['age'])

    return peak_distance_thd




def get_measurements_info(data_directory):
    subjects = get_subjects_metadata()

    data_file_names = os.listdir(data_directory+'.')
    measurements = []
    for fn in data_file_names:
        ssp = fn.split('.')
        if ssp[1] == 'dat':
            measurements.append(ssp[0])

    for m in measurements:
        ssp = m.split('-')
        sn  = ssp[0].upper()
        if not sn in subjects:
            print('No metadata for '+ sn +', skipping: '+m)
            continue
        if 'measurements' in subjects[sn]:
            subjects[sn]['measurements'].append(m)
        else:
            subjects[sn]['measurements'] = [m]

    return subjects


def get_subjects_metadata():
    subjects = {}
#     subject_number_col_idx = 0
#     subject_age_col_idx    = 5
    with open(subject_meta_path, 'r', encoding='utf8') as subjects_csv:
        reader       = csv.reader(subjects_csv)
        header       = next(reader)
        for row in reader:
            subject_number = row[subject_number_col_idx]
            subject_age    = row[subject_age_col_idx]
            if subject_number in subjects:
                print(subject_number+': already have this subject')
                subjects[subject_number][age] = subject_age
            else:
                subjects[subject_number] = {}
                subjects[subject_number]['age'] = int(subject_age)

    return subjects




def dump_to_json( output_file_name, topic, record, window, subjects, idx, idx_neg, signal_segment, time_s):
    Odict = {}
    Odict['topic'] = topic

    Odict['record_Meta'] = {}
    Odict['record_Meta']['name']   = record.record_name

    Odict['segment_meta'] = {}
    Odict['segment_meta']['index']     = idx
    Odict['segment_meta']['index_neg'] = idx_neg
    Odict['segment_meta']['segment_start_time_s'] = time_s 

    Odict['signal_meta'] = {}
    Odict['signal_meta']['signal'] = 'EKG'
    Odict['signal_meta']['window'] = window
    Odict['signal_meta']['frequency_Hz']   = record.fs
    Odict['signal_meta']['unit']           = record.units[channel_of_interest]
    Odict['signal_meta']['resolution_bit'] = record.adc_res[channel_of_interest]
    Odict['signal_meta']['check']          = record.checksum[channel_of_interest]

    subject_number = record.record_name.split('-')[0].upper()
    Odict['subject_meta'] = {}
    Odict['subject_meta']['subject_number'] = subject_number
    Odict['subject_meta']['subject_age']    = subjects[subject_number]['age']
    Odict['subject_meta']['target_HR']      = targetHR - subjects[subject_number]['age']


    fmt = format_switch(Odict['signal_meta']['resolution_bit'],'g')
    signal_segment = np.array(signal_segment)
    signal_segment = np.array2string( signal_segment, max_line_width = float('inf')
                                    , suppress_small = False
                                    , formatter      = {'float_kind':lambda x: fmt % x})
    Odict['signal'] = signal_segment

    with open(output_file_name, 'a+') as outfile:
        json.dump(Odict, outfile)
        outfile.write('\n')


def format_switch(bit_depth,fmt):
    switcher  = {
        32: "%.16"+fmt
      , 16: "%.8"+fmt
      , 10: "%.5"+fmt
      ,  8: "%.4"+fmt
    }

    if bit_depth in switcher:
        return switcher[bit_depth]
    else:
        return "%.20"+fmt



if __name__ == '__main__':
    main()
