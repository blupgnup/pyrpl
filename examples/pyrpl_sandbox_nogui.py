#%% import pyrpl library
from pyrpl import Pyrpl

HOSTNAME="_FAKE_"
#HOSTNAME="192.168.0.158"

# create an interface to the Red Pitaya
p = Pyrpl(config="test", hostname=HOSTNAME, gui=False)

#%% Access the RedPitaya object in charge of communicating with the board
r = p.rp

#check the value of input1
print(r.sampler.in1)

# %% blink some leds for 5 seconds
from time import sleep
for i in range(1025):
    r.hk.led=i
    sleep(0.005)

#%% now feel free to play around a little to get familiar with binary representation by looking at the leds.
from time import sleep
r.hk.led = 0b00000001
for i in range(10):
    r.hk.led = ~r.hk.led>>1
    sleep(0.2)

#%% Module Oscilloscope
s = r.scope # shortcut
print("Available decimation factors:", s.decimations)
print("Trigger sources:", s.trigger_sources)
print("Available inputs: ", s.inputs)


#%% Scope playout

asg = r.asg1
s = r.scope

# turn off asg so the scope has a chance to measure its "off-state" as well
asg.output_direct = "off"

# setup scope
s.input1 = 'asg1'

# pass asg signal through pid0 with a simple integrator - just for fun (detailed explanations for pid will follow)
r.pid0.input = 'asg1'
r.pid0.ival = 0 # reset the integrator to zero
r.pid0.i = 1000 # unity gain frequency of 1000 hz
r.pid0.p = 1.0 # proportional gain of 1.0
r.pid0.inputfilter = [0,0,0,0] # leave input filter disabled for now

# show pid output on channel2
s.input2 = 'pid0'

# trig at zero volt crossing
s.threshold_ch1 = 0

# positive/negative slope is detected by waiting for input to
# sweep through hysteresis around the trigger threshold in
# the right direction
s.hysteresis_ch1 = 0.01

# trigger on the input signal positive slope
s.trigger_source = 'ch1_positive_edge'

# take data symetrically around the trigger event
s.trigger_delay = 0

# set decimation factor to 64 -> full scope trace is 8ns * 2^14 * decimation = 8.3 ms long
s.decimation = 64

# launch a single (asynchronous) curve acquisition, the asynchronous
# acquisition means that the function returns immediately, eventhough the
# data-acquisition is still going on.
res = s.curve_async()

print("Before turning on asg:")
print("Curve ready:", s.curve_ready()) # trigger should still be armed

# turn on asg and leave enough time for the scope to record the data
asg.setup(frequency=1e3, amplitude=0.3, start_phase=90, waveform='halframp', trigger_source='immediately')
sleep(0.010)

# check that the trigger has been disarmed
print("After turning on asg:")
print("Curve ready:", s.curve_ready())

print("Trigger event age [ms]:",8e-9*((
s.current_timestamp&0xFFFFFFFFFFFFFFFF) - s.trigger_timestamp)*1000)

#%% DOES NOT WORK IF LAUNCHED STRAIGHT AWAY ?
# The function curve_async returns a *future* (or promise) of the curve. To
# access the actual curve, use result()
ch1, ch2 = res.result()

#%% plot the data
%matplotlib inline
plt.plot(s.times*1e3, ch1, s.times*1e3, ch2)
plt.xlabel("Time [ms]")
plt.ylabel("Voltage")

#%% Test software manager
# directly accessing the scope will not *reserve* it
scope = p.rp.scope
print(scope.owner)
scope.duration = 1.

# using the scope manager changes its ownership
with p.scopes.pop('Myself') as scope:
   print(scope.owner)
   scope.duration =0.01
   print(scope.duration)
# The scope is freed (and reset to its previous state) after the with
# construct
print(scope.owner)
print(scope.duration)

#%% useful functions for scope diagnostics
print("Curve ready:", s.curve_ready())
print("Trigger source:",s.trigger_source)
print("Trigger threshold [V]:",s.threshold_ch1)
print("Averaging:",s.average)
print("Trigger delay [s]:",s.trigger_delay)
print("Trace duration [s]: ",s.duration)
print("Trigger hysteresis [V]", s.hysteresis_ch1)
print("Current scope time [cycles]:",hex(s.current_timestamp))
print("Trigger time [cycles]:",hex(s.trigger_timestamp))
print("Current voltage on channel 1 [V]:", r.scope.voltage_in1)
print("First point in data buffer 1 [V]:", s.ch1_firstpoint)
