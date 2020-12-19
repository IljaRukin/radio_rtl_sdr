import asyncio
from rtlsdr import RtlSdr
import numpy as np
from math import nan,isnan,floor,ceil
from scipy.ndimage import gaussian_filter1d as gaussian
from time import sleep

global pi,i
pi =np.pi
i = np.complex(0,1)

abs2 = lambda x: np.square(np.real(x)) + np.square(np.imag(x))
phase_diff = lambda x: np.diff(np.imag(x))*np.real(x)[1:] - np.diff(np.real(x))*np.imag(x)[1:]

sequence = ['00100101110000100010010111','00101101110111100010110111','01000011101110100100001110','01000111101101000100011110','00011010111001000001101011','01001110101100000100111010','10100111110110001010011111','11101111000100101110111100']

async def streaming():
	freq = 933.6e+6 #mhz #ch49: 944.8mhz - 637hz ch1: 935.2mhz - 320Hz ch6: 936.2mhz - 502hz ch3: 935.6mhz - 1.083khz ch45: 944.0mhz - 12.542khz 
	sample_rate = 270844.16710001737*5 #285000,1140000,2280000
	bandwidth = 200e+3
	burst_time = 576.9e-6 #burst time
	burst_symbols = 156.25 #bits per burst
	bps = burst_symbols/burst_time #bits per second
	sample_per_burst = sample_rate*burst_time #samples per burst
	sample_per_bit = sample_per_burst/burst_symbols #samples per bit

	sdr = RtlSdr()
	sleep(1)
	sdr.sample_rate = sample_rate
	sdr.center_freq = freq
	sdr.bandwidth = bandwidth
	sdr.freq_correction = 50 #PPM
	sdr.gain = 40 #'auto' #35

	remaining = np.array([0 + 0*i],dtype=np.complex)
	async for samples in sdr.stream():
		samples = np.concatenate((remaining,samples))

		#find power increase of signal (start of burst)
		mask = abs2(samples)
		nr_samples = mask.size
		mask = mask>np.sum(mask)*0.3/(nr_samples)
		start_points_candidate = np.where(np.diff(mask))[0]
		ind = (start_points_candidate[1:]-start_points_candidate[:-1])>0.5*sample_per_burst
		start_points = list( start_points_candidate[np.where(ind)] )

		#extract data
		for p in start_points:
			a = p+int(sample_per_bit)
			b = p+int(sample_per_burst)
			#decode
			samp = samples[a:b]
			s = np.argmin(np.diff(abs2(samp)))
			samp = samp[:s]
			phase = np.angle(samp)
			unwrap = np.unwrap(phase,discont=pi)
			slope = np.diff(unwrap)
			smooth = unwrap - s* (slope.max() + slope.min())/2 #equal -min = max slope
			#smooth = gaussian(smooth,0.2)
			phase_change = np.gradient(smooth)
			digital = phase_change > np.sum(phase_change)/(b-a)
			bits = np.round( np.diff(np.where(np.diff(digital))[0]) / sample_per_bit ).astype(int)
			result = np.zeros(np.ceil(s/sample_per_bit).astype(int))
			pos = 0
			bit = True
			for l in bits:
				result[pos:pos+l] = bit
				bit ^= 1
				pos += l
			
			#process
			result = str((result)).replace(',','').replace('.','').replace(' ','').replace('\n','').replace('[','').replace(']','')
			#print(result)
			for string in sequence:
				if result.find(string) != -1:
					print(result)
			break

		remaining = samples[p+int(sample_per_burst):]
	# to stop streaming:
	await sdr.stop()

	# done
	sdr.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())