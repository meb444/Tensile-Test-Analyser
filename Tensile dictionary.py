# The goal of this program is to export a file containing graphs and useful information from a tensile test
# This program was written for data from an Instron Universal Testing Machine using Bluehill testing prgrams,
# exported to the user as a csv file
# Notes are made where hard coding was performed to collect data, and as needed the columns data are pulled from can be
# changed
# It should be noted that conversion of units is not currently supported, although that is a plan for future work
# A more comprehensive user interface with prompts is also a consideration for future development
# Other future modifications include having a better data type, removing unneeded operations, and cleaning up variables

# Adding needed imports for code to run - if your computer does not have them please download as needed
import csv
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import stats

# The first step is to read in the file. Please provide the complete file path between the quotation marks below
# Do NOT DELETE the 'r' in front of the quotes
file = r"C:\Users\megan\OneDrive\Documents\Research Spring 2020\vERTICLAab_fEB20_2020.is_tens_RawData\Specimen_RawData_11.csv"
# empty array the file will be read into
data = []
# Reads in file to the array data
# Note that all values in the use_data array will be strings and must be cast to float
# before operations can be performed (This operation is performed in later steps)
with open(file) as csvfile:
    reader = csv.reader(csvfile, csv.QUOTE_NONNUMERIC)
    for row in reader:
        data.append(row)

# Creates an array with the name and key constand values for the specimen
dimen = [data[0][1], float(data[7][1]), float(data[4][1]),
         float(data[5][1])]  # name, extensometer length, width, thickness
print(dimen)

# Adds values to the dictionary. Key is what number data point this is, starting at zero
# tensile extension, load, strain (tensile extension/extensometer length), stress (load/1000/width/thickness)
# (converts psi to ksi), strain offset (strain + 0.002)
dct = {}
i = 0
for row in range(12, len(data)):
    each = data[row]
    dct[i] = [float(each[3]), float(each[4]), float(each[3]) / dimen[1], float(each[4]) / dimen[2] / dimen[3] / 1000,
              (float(each[3]) / dimen[1]) + 0.002]
    # print(dct[i])
    i += 1
# print(dct)
# print('test', dct[45][4])

# This causes every 25th dictionary key number (0, 25, 50, ect) to have a 5th index of slope, which is the LSR line of
# that index and the next 200 elements
# This slope is calculated using the offset strain (x values) and stress (y values)
cont = True
i = 0
while cont:
    slope_strain_offset = []
    slope_stress = []
    j = i
    while j < i + 200 and dct.get(j, 0) != 0:
        slope_strain_offset.append(dct[j][4])
        slope_stress.append(dct[j][3])
        j += 1
    if len(slope_stress) != 0 or len(slope_strain_offset) != 0:
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(slope_strain_offset, slope_stress)
        #print(slope)
        dct[i].append(slope)
    # print(dct[i])
    i += 25
    if i > len(dct):
        cont = False

#print(dct)

# Adding standard deviations for each group of 8
#print('std deviations now')
for i in range(0, len(dct), 25):
    end = 0
    std_dev = []
    for j in range(i, i +200, 25):
        if(dct.get(j, 0) == 0):
            break
        else:
            end = j
            std_dev.append(dct[j][5])
    if len(std_dev) == 8:
        dct[i].append(np.std(std_dev))
        dct[i].append(end)
        #print(dct[i][6])

key_large_slope_dec = 0

for i in range(200, len(dct), 25):
    # print(i, 'prev slope', dct[i-200][5], 'cur slope', dct[i][5])
    if dct[i-200][5] > 2*dct[i][5]:
        key_large_slope_dec = i
        break
print('key', key_large_slope_dec)
print('len dct', len(dct))


# Finding mimimum stddev in ocurances up to point where the slope decreases by at least 50%
min = dct[0][6]
min_key = 0
for i in range(25, key_large_slope_dec, 25):
    if dct[i][6] < min:
        min = dct[i][6]
        min_key = i
print('min key', min_key, 'min std dev', min, 'end std dev key', dct[min_key][7])

# Trying to get slope from the range produced here
point_two_line_strain = []
point_two_line_stress = []

# Adds data that influenced the standard deviation - from the start key to 200 data points beyond the end key
# Then calulates and prints LSR line
for i in range(min_key, min_key+200):
    point_two_line_strain.append(dct[i][4])
    point_two_line_stress.append(dct[i][3])
print(len(point_two_line_stress))
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(point_two_line_strain, point_two_line_stress)
print('y = ', slope, 'x +', intercept)
print('name', dimen[0])

# I do want to draw from a larger range than this is producing, so add more data if the next slope is +\- 12.5%
# this slope
# Start at 225 which is next calculated slope in the dictionary
# Goes to i +201 to get all data included
# Is not looking before start index I don't think this is an issue
j_ran_at = 0
for i in range(min_key + 225, len(dct), 25):
    if 1.125*slope >= dct[i][5] >= 0.775*slope:
        # Add to i to get the current values. At last run (how do we get this? We want to add all 200 elements
        for j in range(i-25, i):
            j_ran_at = i
            point_two_line_stress.append(dct[i][3])
            point_two_line_strain.append(dct[i][4])
        # print('len', len(point_two_line_stress))
        # print('i', i)
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(point_two_line_strain, point_two_line_stress)
print('y = ', slope, 'x +', intercept)
print('name', dimen[0])
# Creates stress - strain arrays for plotting based off the dct values
stress = []
strain = []
stress_calc = []
strain_short = []

for i in range(0, len(dct)):
    strain.append(dct[i][2])
    stress.append(dct[i][3])
    if slope*dct[i][2]+intercept >= 0 and dct[i][2] <= 0.005: # If the stress is positive and the strain is less than 0.005
        stress_calc.append(slope*dct[i][2]+intercept)
        strain_short.append(dct[i][2])
# Plots the stress - strain curve with offset line
# Pauses code until closed
plt.plot(strain, stress)
plt.plot(strain_short, stress_calc)
plt.xlabel('Strain')
plt.ylabel('Stress (ksi)')
plt.title('Stress Vs. Strain with 0.002% offset line')
# Displays Plot, code will pause until plot is closed
plt.show()

# finding stress and strain at 0.02% offset
# Find closest two values between stress and stess calc
# Subtract, absolute value, minimum
stress_dif = np.abs(stress[0]-(slope*strain[0]+intercept))
offset_key = 0
for i in range(1, len(strain)):
    if np.abs(stress[i]-(slope*strain[i]+intercept)) < stress_dif:
        stress_dif = np.abs(stress[0]-stress_calc[0])
        offset_key = i+1
offset_stress = dct[offset_key][3]
offset_strain = dct[offset_key][2]
print('offset stress', offset_stress, 'and strain', offset_strain)
# Easy calculations now

# Ultimate tensile strength (max stress)
UTS = dct[0][3]
UTS_Strain = dct[0][2]
for i in range(1, len(dct)):
    if dct[i][3] > UTS:
        UTS = dct[i][3]
        UTS_Strain = dct[i][2]
print("UTS", UTS, "Corresponding strain", UTS_Strain)

# Max Elongation (max strain)
elongation = dct[0][2]
stress_elongation = dct[0][3]
for i in range(1, len(dct)):
    if dct[i][2] > elongation:
        elongation = dct[i][2]
        stress_elongation = dct[i][3]
print("max elongation", elongation, 'correponding stress', stress_elongation)

