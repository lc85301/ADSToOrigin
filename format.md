ADSToOrigin explanation
=======================

1. rectangle plot format
------------------------
### format dump by ADS
sweepvar[1] ... sweepvar_n-1] sweepvar[n] data   
var[1][1]    ... var[n-1][1]     var[n][1]    data[1][1]  
var[1][1]    ... var[n-1][1]     var[n][2]    data[1][2]  
var[1][1]    ... var[n-1][1]     var[n][3]    data[1][3]  
...  
var[1][1]    ... var[n-1][1]     var[n][m]    data[1][m]  
  
sweepvar[1] ... sweepvar[n-1] sweepvar[n] data     
var[1][1]    ... var[n-1][2]     var[n][1]    data[2][1]  
var[1][1]    ... var[n-1][2]     var[n][2]    data[2][2]  
var[1][1]    ... var[n-1][2]     var[n][3]    data[2][3]  
...  
var[1][1]    ... var[n-1][2]     var[n][m]    data[2][m]  
...  
------
### transfer into origin
sweepvar[n] sweepvar[1]=var[1][1],...sweepvar[n-1]=var[n-1][1] sweepvar[1]=var[1][1],...sweepvar[n-1]=var[n-1][2] ...  
var[n][1]    data[1][1]    data2][1]  
var[n][2]    data[1][2]    data2][2]  
var[n][3]    data[1][3]    data2][3]  
...  
var[n][m]    data[1][m]    data2][m]  
------

2. smith chart plot:
--------------------
### format dump by ADS
sweepvar data[1]  
var[1]     data[1][1]mag / data[1][1]phase  
var[2]     data[1][2]mag / data[1][2]phase  
var[3]     data[1][3]mag / data[1][3]phase  
...  
var[n]     data[1][n]mag / data[1][n]phase  
  
sweepvar data[2]  
var[1]     data[2][1]mag / data[2][1]phase  
var[2]     data[2][2]mag / data[2][2]phase  
var[3]     data[2][3]mag / data[2][3]phase  
...  
var[n]     data[2][n]mag / data[2][n]phase  
...  
------
### transfer into origin
sweepvar data1_real       data1_imag       data2_real       data2_imag  
var[1]   data[1][1]real   data[1][1]imag   data[2][1]real   data[2][1]imag  
var[2]   data[1][2]real   data[1][2]imag   data[2][2]real   data[2][2]imag  
var[3]   data[1][3]real   data[1][3]imag   data[2][3]real   data[2][3]imag  
...  
var[n]   data[1][n]real   data[1][n]imag   data[2][n]real   data[2][n]imag  
------

3. magnitude/phase to real/imag:
--------------------------------
### formula:

Gamma = mag * exp(j*phase) = R+jX  
Z = r+j*x = Z0 * (1+gamma)/(1-gamma)  
for convenience in origin, Z0 = 1  
phase record in degree  

r = (1-R^2-X^2) / (1-2R+R^2+X^2)  
x = (2*X) / (1-2R+R^2+X^2)  
