import asyncio
from rtlsdr import RtlSdr
from scipy.signal import decimate
import numpy as np
import sounddevice as sd

async def streaming():
	freq = 89.8e6 #mhz
	sample_rate = 285000 #285000,1140000,2280000
	bandwidth = 180e+3

	sdr = RtlSdr()
	sdr.sample_rate = sample_rate
	sdr.center_freq = freq
	sdr.bandwidth = bandwidth
	sdr.freq_correction = 50 #PPM
	sdr.gain = 'auto'

	volume = 0.02 #multiplier
	sound_decimate = int(sample_rate/44100)
	sound_sample_rate = sample_rate/sound_decimate
	audio = sd.OutputStream(channels=1,samplerate=sound_sample_rate)
	audio.start()

	async for samples in sdr.stream():
		freq = np.real(samples)[1:]*np.diff(np.imag(samples)) - np.imag(samples)[1:]*np.diff(np.real(samples))
		freq = decimate(freq,sound_decimate)
		freq = volume*freq
		#sd.play(freq,sound_sample_rate) #slow api for playback
		audio.write(freq.astype('float32'))

	# to stop streaming:
	await sdr.stop()

	# done
	sdr.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())