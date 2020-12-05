import numpy as np
from bisect import bisect

a = np.array([[1,1,1,1,1,1,1,1],[2,2,2,2,2,2,2,2],[3,3,3,3,3,3,3,3]])
b = np.array([[2,2,2,5,5,5,2,2]])
c = a*b
print(c)
d = np.array([[1],[1],[1],[1],[1],[1],[1],[1]])
e = np.dot(c,d)
print(e)


x = 12
ranges = [0, 46, 91, 136, 181, 226, 271,316]
microphones = [5,4,3,2,1,0,7,6]
if x <= 360:
    x = bisect(ranges,x)
    
else:
    print('Out of bounds')

print("microphone of x is "+str(microphones[x-1]))