# radio_rtl_sdr
experiments with radio signal modulation and decoding

## radio.py
is a script to play fm radio in real time using a rtl sdr stick.

## radio_advanced.py
i tried different filters to improve sound quality, most of them are not used and commented out in the python script.
at the end the best result was achieved with specified gain (not auto), a simple low pass and an offset correction by a moving window.

## gsm.py
is a script to gecode gsm and print bursts, if they contain a specific sequence.
unfortunately the calculation is quite slow, hence the script is not suitable for real time application.

## modulation.ipynb
describes the most important modulation types (amplitude,phase,frequency,qam) and has simple implementations to decode them

## decode_radio.ipynb
has step by step visualizations of how the fm radio decoding is done

## decode_gsm.ipynb
overview and first steps to decode gsm mobile signals including a simulation.

## gsm_stream_decode.ipynb
more visualizations and decoding of separate bursts from start to finish.

## folder: gr_gsm_experiments
experiments done with gnuradio and gr_gsm using dragonOS (by cemaxecuter) to capture and decode some data.
