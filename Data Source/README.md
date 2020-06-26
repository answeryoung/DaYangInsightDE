## Data Source
The original dataset is collected and processed by
Vera Novak, Kun Hu, Laura Desrochers, Peter Novak, Louis Caplan, Lewis Lipsitz, and Magdy Selim (2010). Cerebral flow velocities during daily activities depend on blood pressure in patients with chronic ischemic infarctions. Stroke; a Journal of Cerebral Circulation, 41(1), 61–66. http://doi.org/10.1161/STROKEAHA.109.565556.

It is available on PhysioNet.org at
[https://physionet.org/content/cves/1.0.0/](https://physionet.org/content/cves/1.0.0/)

The files was downloaded to an EC-2 instance with a 240 GB storage attached. The set of files can be downloaded with this command:

    wget -r -N -c -np https://physionet.org/files/cves/1.0.0/

## Data Pre-processing for This Project
The .json files were created using [Preprocessing2.py](Preprocessing2.py)
Overall, the set of .json files is a data set suited to simulate a data stream of identical schema at a frequency of up to 10,000 messages per second and a speed of up to 250 Mbps.
