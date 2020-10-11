#
# sample app for Gaussian blurring, used to understand an algorithm
# I was considering using to simplify maps produced for Foundation export.
#
from math import exp

def gaussian(x, mu, sigma):
  return exp( -(((x-mu)/(sigma))**2)/2.0 )

#kernel_height, kernel_width = 7, 7
kernel_radius = 3 # for an 7x7 filter
sigma = kernel_radius/2. # for [-2*sigma, 2*sigma]

# compute the actual kernel elements
hkernel = [gaussian(x, kernel_radius, sigma) for x in range(2*kernel_radius+1)]
vkernel = [x for x in hkernel]
kernel2d = [[xh*xv for xh in hkernel] for xv in vkernel]

# normalize the kernel elements
kernelsum = sum([sum(row) for row in kernel2d])
kernel2d = [[x/kernelsum for x in row] for row in kernel2d]

print("Basic 2D R=3")
for line in kernel2d:
  print ["    %.5f" % x for x in line]


print("")

# now produce a 1D kernel
kernelsum = sum(hkernel)
kernel1d = [x/kernelsum for x in hkernel]

print("Basic 1D R=3")
print ["    %.5f" % x for x in kernel1d]

print("")

# now compute a 2D kernel from the 1D kernel
calc2d =[]
for i in range(7):
    row = []
    for j in range(7):
        row.append(kernel1d[i] * kernel1d[j])
    calc2d.append(row)

print("Associatively Calculated 2D R=3")
for line in calc2d:
  print ["    %.5f" % x for x in line]
