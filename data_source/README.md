## Data Source
The original dataset is collected and processed by
Vera Novak, Kun Hu, Laura Desrochers, Peter Novak, Louis Caplan, Lewis Lipsitz, and Magdy Selim (2010). Cerebral flow velocities during daily activities depend on blood pressure in patients with chronic ischemic infarctions. Stroke; a Journal of Cerebral Circulation, 41(1), 61-66. http://doi.org/10.1161/STROKEAHA.109.565556.

It is available on PhysioNet.org at
[https://physionet.org/content/cves/1.0.0/]( https://physionet.org/content/cves/1.0.0/)

The files was downloaded to an EC-2 instance with a 240 GB storage attached. The set of files can be downloaded with this command:

    wget -r -N -c -np https://physionet.org/files/cves/1.0.0/

## Data Pre-processing for This Project
The original dataset has ECG waveforms from many measurements, typically hours worth of waveform, from over 90 patients.

Each measurement is break into pieces.
Each piece has about 15 min. worth of ECG signals, and is considered as a patient for this data source.
Each of those 15 min. pieces is further dived into segments, each of which corresponds to R-peak-to-R-peak heartbeat.
Each segment is wrapped in json structure and stored, with other segments from the patient, in a .json file.
This is done by [preprocessing.py]( preprocessing.py).

Overall, the set of .json files is a data set suited to simulate a data stream of identical schema at a frequency of up to 10,000 messages per second and a speed of up to 250 Mbps.
When my algorithm didn't find an R-peak in a long segment from a 15 min. piece of signal, the signal is written as something like `"[1355 1353 1340 ... 1239 1278 1301]"`.
