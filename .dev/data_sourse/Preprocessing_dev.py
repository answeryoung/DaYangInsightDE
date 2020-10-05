import os
import sys
import csv
import json
import numpy as np

from scipy.signal import find_peaks
import wfdb

data_dir = 'ecg-data/'
subject_meta_path = 'ecg-data/subjects.csv'

output_json_name = 'ecg-data.json'

targetHR = 220;
sample_length = 15*60;
min_sample_lenght = 30;

subject_number_col_idx = 0
subject_age_col_idx    = 5

subjects = {}
subjects_csv = open(subject_meta_path, encoding='utf8')
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

subjects_csv.close()

file_names = os.listdir(data_dir+'.')


measurements = []
for fn in file_names:
    ssp = fn.split('.')
    if ssp[1] == 'dat':
        measurements.append(ssp[0])

for m in measurements:
    ssp = m.split('-')
    sn  = ssp[0].upper()
    if not sn in subjects:
    	print('No metadat for '+ sn +', skipping: '+m)
    	continue
    if 'measurements' in subjects[sn]:
        subjects[sn]['measurements'].append(m)
    else:
        subjects[sn]['measurements'] = [m]

c = -1
for s in subjects:
    if 'measurements' in subjects[s]:
        print(s)
        for m in subjects[s]['measurements']:
            print('  '+m)
            record = wfdb.rdrecord(data_dir+m) 
            signal_whole = record.p_signal[:,0]
            if len(signal_whole) < min_sample_lenght*record.fs:
            	print('    '+m +' is too shork, skipping..')
            	continue
                        
            peak_distance_thd = 60*record.fs/(targetHR - subjects[s]['age'])

            window_width = sample_length*record.fs
            nWindow      = np.round(len(signal_whole)/window_width)
            if nWindow == 0:
                nWindow = 1
                window_width = len(signal_whole)
            else:
                window_width = int(np.floor(len(signal_whole)/nWindow))
                nWindow      = int(nWindow)
			
            for w in range(nWindow):
                c += 1
                topic = 'ecg-'+str(c).zfill(6)
                print(topic)
                signal     = signal_whole[(w*window_width):((w+1)*window_width)]
                ptp_value  = np.ptp(signal)

                subwindow_width = 3*record.fs
                nSubwindow      = np.round(len(signal)/subwindow_width)
                subwindow_width = int(np.floor(len(record.p_signal[:,0])/nSubwindow))
                nSubwindow      = int(nSubwindow)

                for sw in range(nSubwindow):
                    subsignal = signal_whole[sw*subwindow_width:(sw+1)*subwindow_width]
                    ptp_sub   = np.ptp(subsignal)
                    if ptp_value > ptp_sub:
                        ptp_value = ptp_sub

                prominence_thd    = 0.35*ptp_value
                peaks, properties = find_peaks(signal, prominence=prominence_thd
                                               , distance=peak_distance_thd)
                    
                nPeaks = len(peaks)
                if len(peaks) == 0:
                    print('      No peak found in '+ m +':'+str(w)+', skipping..')
                    continue

                sample = signal[0:peaks[0]].tolist()
                Odict = {}
                Odict['topic'] = topic

                Odict['record_Meta'] = {}
                Odict['record_Meta']['name'] = record.record_name
                Odict['record_Meta']['signal'] = 'EKG'
 			
                Odict['segment_meta'] = {}
                Odict['segment_meta']['index']   = w
                Odict['segment_meta']['isFirst'] = True
                Odict['segment_meta']['isLast']  = False

                Odict['signal_meta'] = {}
                Odict['signal_meta']['frequency_Hz'] 	= record.fs
                Odict['signal_meta']['unit'] 		= record.units[0]
                Odict['signal_meta']['resolution_bit'] 	= record.adc_res[0]
                Odict['signal_meta']['check'] 	        = record.checksum[0]

                Odict['subject_meta'] = {}
                Odict['subject_meta']['subject_number'] = s
                Odict['subject_meta']['subject_age'] = subjects[s]['age']
                Odict['subject_meta']['target_HR'] = targetHR - subjects[s]['age']

                Odict['signal'] = str(sample)

                if c == 0:
                    with open(output_json_name, 'w') as outfile:
                        json.dump(Odict, outfile)
                        outfile.write('\n')
                else:
                    with open(output_json_name, 'a') as outfile:
                        json.dump(Odict, outfile)
                        outfile.write('\n')
						
                isLast  = False
                for p in range(nPeaks):   
                    if p < nPeaks - 1:
                        sample = signal[peaks[p]:peaks[p+1]].tolist();
                    else:
                        sample = signal[peaks[p]:-1].tolist();
                        isLast = True

                    Odict = {}
                    Odict['topic'] = 'ecg-'+str(c).zfill(6)

                    Odict['record_Meta'] = {}
                    Odict['record_Meta']['name'] = record.record_name
                    Odict['record_Meta']['signal'] = 'EKG'

                    Odict['segment_meta'] = {}
                    Odict['segment_meta']['index'] = w
                    Odict['segment_meta']['isFirst'] = False
                    Odict['segment_meta']['isLast']  = isLast

                    Odict['signal_meta'] = {}
                    Odict['signal_meta']['frequency_Hz']   = record.fs
                    Odict['signal_meta']['unit']           = record.units[0]
                    Odict['signal_meta']['resolution_bit'] = record.adc_res[0]
                    Odict['signal_meta']['check']          = record.checksum[0]

                    Odict['subject_meta'] = {}
                    Odict['subject_meta']['subject_number'] = s
                    Odict['subject_meta']['subject_age'] = subjects[s]['age']
                    Odict['subject_meta']['target_HR'] = targetHR - subjects[s]['age']

                    Odict['signal'] = str(sample)
				
