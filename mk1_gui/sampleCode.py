import matplotlib.pyplot as plt
import numpy as np
import time

fig, ax = plt.subplots()
line, = ax.plot(np.random.randn(1000))
# plt.setp(line, aa=False)

tstart = time.time()
num_plots = 0
while time.time()-tstart < 1:
    line.set_ydata(np.random.randn(1000))
    plt.pause(0.001)
    num_plots += 1
print(num_plots)