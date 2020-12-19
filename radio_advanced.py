import asyncio
from rtlsdr import RtlSdr
from scipy.signal import decimate,butter,sosfilt
import numpy as np
import sounddevice as sd
from time import sleep

global pi,i
pi =np.pi
i = np.complex(0,1)

abs2 = lambda x: np.square(np.real(x)) + np.square(np.imag(x))
#phase_diff = lambda x: np.diff(np.angle(x))
phase_diff = lambda x: np.diff(np.imag(x))*np.real(x)[1:] - np.diff(np.real(x))*np.imag(x)[1:]

def normalize_average(x):
	xx = np.abs(x)
	summed = np.sum(xx)
	length = np.size(xx)
	loudness = summed/length
	return x*(1/loudness)

def normalize_upper(x):
	xx = np.abs(x)
	top = xx[np.where(xx > 0.8*np.max(xx))[0]]
	summed = np.sum(top)
	length = np.size(top)
	loudness = summed/length
	return x*(1/loudness)*0.05

async def streaming():
	###sdr settings
	freq = 89.8e+6 #mhz
	sample_rate = 1140000 #285000,1140000,2280000
	bandwidth = 160e+3

	###setup sdr
	sdr = RtlSdr()
	sleep(1)
	sdr.sample_rate = sample_rate
	sdr.center_freq = freq
	sdr.bandwidth = bandwidth
	sdr.freq_correction = 60 #PPM
	sdr.gain = 25 #'auto'

	###zero ofset
	nr_samples = 2**17 #number of samples per loop under ideal conditions!
	window = 4096 #for setting audio signal to zero
	step = int(nr_samples/window)

	###low pass filter
	sos = butter(8, 45e+3, 'low', fs=sample_rate, output='sos') #generate low pass filter

	###audio
	volume = 200 #multiplier
#	prev_loudness = volume
	audio_sample_rate = 44100 #prefered audio sample rate
	sound_decimate = int(sample_rate/audio_sample_rate)
	sound_sample_rate = sample_rate/sound_decimate
	audio = sd.OutputStream(channels=1,samplerate=sound_sample_rate)
	audio.start()

	async for samples in sdr.stream():
		###demodulate sound
		sound = phase_diff(samples)
		
		###set sound frequency to zero with a moving window
		for iii in range(window):
			sound[step*iii:step*(iii+1)] = sound[step*iii:step*(iii+1)] - np.sum(sound[step*iii:step*(iii+1)])/window
		
		###low pass filter
		sound = sosfilt(sos, sound)
		
		###reduce sample count
		sound = decimate(sound,sound_decimate)
		
		###normalize average of sound (beware offset)
#		sound = normalize_average(sound) #average volume normalization
	
		###adaptive sound volume
#		next_loudness = np.sum(sound)/np.size(sound) * 1/volume
#		next_loudness += 0.00000001*(prev_loudness-next_loudness)
#		sound = sound*(1/next_loudness)
#		prev_loudness = next_loudness
		
		###reduce volume
		sound = sound*volume

		###play sound
		#sd.play(sound,sound_sample_rate) #slow api for playback
		audio.write(sound.astype('float32'))

	# to stop streaming:
	await sdr.stop()

	# done
	sdr.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())
