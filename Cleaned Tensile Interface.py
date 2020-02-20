# The goal of this program is to export a file containing graphs and useful information from a tensile test
# This program was written for data from an Instron Universal Testing Machine using (?? Dolphin testing system??),
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
file = r"C:\Users\megan\OneDrive\Documents\Research Spring 2020\TestOneVert.is_tens_RawData\Specimen_RawData_1.csv"
# empty array the file will be read into
data = []
# Reads in file to the array data
# Note that all values in the use_data array will be strings and must be cast to float
# before operations can be performed (This operation is performed in later steps)
with open(file) as csvfile:
    reader = csv.reader(csvfile, csv.QUOTE_NONNUMERIC)
    for row in reader:
        data.append(row)
# Converts data to a numpy array, allowing for better manipulation and calculations
# Note data is an array filled with arrays containing string values, and will be further split into named arrays with
# float values for ease of following the code (not for computing speed but IDK what I'm doing yet)
use_data = np.asarray(data)


# User defined function to assign dimensions to a fixed index in an array
# The width, thickness, and extensometer length will be pulled from the datasheet - note it is hard coded!
# But can be user overridden
# Non specified dimensions will be set to 0.0
def dimensions(gage_length=0.0, width=0.0, thickness=0.0, extensometer_length=0.0, a_length_reduced=0.0,
               b_length_grip=0.0, c_width_grip=0.0,
               l_overall_length=0.0):
    if extensometer_length == 0.0:
        extensometer_length = float(use_data[7][1])
    if width == 0.0:
        width = float(use_data[4][1])
    if thickness == 0.0:
        thickness = float(use_data[5][1])
    dimen = [gage_length, width, thickness, extensometer_length, a_length_reduced, b_length_grip, c_width_grip,
             l_overall_length]
    return dimen


# Here is where tensile dimensions can be changed if needed. If not entering values in all the dimensions, use the name
# of the variable followed by an equal sign and the number (no spaces) to set just that value - order does not matter
# BECAUSE THIS WILL NOT CHANGE WITH EACH SUCCESSIVE FILE, MAKE SURE TO REMOVE ANY CHANGES IF THEY DO NOT APPLY FOR THE
# NEXT DATASET
tensile_dimensions = dimensions(1, .086, c_width_grip=.434, b_length_grip=.5)
# Prints out tensile dimensions so user can check that they match the actual dimensions
print("final tensile dimensions:", tensile_dimensions)


# Function to compute cross sectional area given array of dimensions
def cross_sec_area(dimen):
    return dimen[1] * dimen[2]


# Creates empty arrays which stress, strain, and offset strain (strain +0.002, not completely needed but useful)
strain = []
stress = []
strain_offset = []

# Iterates over the the data from 12 (starting index with values) to the end of the list of data, adding to the stress
# and strain and offset strain arrays
# The strain is calculated using the tensile extension divided by the extenstometer gage length
# Offset strain is the same function as current strain + 0.002
# The stress is calculated using the force (lbf) divided by cross sectional area divided by 1000, has units kilopounds
# per square inch
# Each value from use_data is cast to a float type to allow for the math operations
for rows in range(12, len(use_data) - 1):
    strain.append(float(use_data[rows][3]) / tensile_dimensions[3])
    strain_offset.append(float(use_data[rows][3]) / tensile_dimensions[3] + .002)
    stress.append(float(use_data[rows][4]) / cross_sec_area(tensile_dimensions) / 1000)

# Plotting the stress vs. strain data
# If change units y-axis label will need to be changed
plt.plot(strain, stress)
plt.xlabel('Strain')
plt.ylabel('Stress (ksi)')
plt.title('Stress Vs. Strain')
# Displays Plot, code will pause until plot is closed
plt.show()


# This method will check the slopes to see if we are in a linear region, and return a counter indicating how many times
# the slope has decreased consecutively
# we want to check to see if we have departed the linear region, and if we have, we want to break out of the loop
# If the slope decreased from the previous slope the counter is incremented - this may indicate a departure from
# linearity
# If the slope is not less than the previous slope, reset counter to zero to ensure that we don't accidentally
# end the loop early and miss some of the linear portion
def check_slopes(slopes, counter):
    cur_slope = slopes[len(slopes) - 1]
    if cur_slope < slopes[len(slopes) - 2]:
        counter += 1
    else:
        counter == 0
    return counter


# This function returns an array of slopes for a least squares regresion line (LSR) for each group of 200 data points
# This function calls the
# Nested for loop
# Outer loop steps through the stress and strain values, moving in steps of 25
# Inner for loop steps through the current index (i) of the outer for loop to i+200 or the end of the file, whichever
# is first
# NOTE: At this time, the return statement is pointless because the gobal variables have same name and are updated
# during the method
def lsr_slope_sections():
    slopes = []
    start = []
    counter_slope = 0
    for i in range(0, len(stress) - 1, 25):
        this_group_x = []
        this_group_y = []
        start.append(i)
        # print("X", this_group_x)
        # print("Y", this_group_y)
        for each in range(i, i + 200):
            if each >= len(stress):
                break
            this_group_x.append(strain_offset[each])
            this_group_y.append(stress[each])
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(this_group_x, this_group_y)
        slopes.append(slope)
        counter_slope = check_slopes(slopes, counter_slope)
        # Break point is set to twenty-five. If this is too small (ie there is not a clear drop in slopes then it
        # should be increased, that number can be changed
        if counter_slope > 25:
            break
    # print(slopes_LSR)
    return [slopes, start]


slope_and_index = lsr_slope_sections()
# arrays for values associated with the various LSR lines created in loop
slopes_LSR = slope_and_index[0]
# Array of start index for each calculated LSR line
start_index = slope_and_index[1]
#print(slopes_LSR)
#print(start_index)

# This code creates an array of the differences between adjacent slopes
# The next step is to find the smallest difference between two consecutive slopes - this will be taken as the center of
# the most linear portion. Note this can cause errors if the data contains deviations from the standard curve
# Future work may try to fix this issue
# Fills the slope difference array, taking the absolute value of the difference to make minimum difference searchable
# Slope difference array
slope_dif = []
# Fills the slope difference array, taking the absolute value of the difference to make minimum difference searchable
for i in range(0, len(slopes_LSR) - 2):
    cur_slope_dif = slopes_LSR[i] - slopes_LSR[i + 1]
    slope_dif.append(abs(slopes_LSR[i] - slopes_LSR[i + 1]))
# Finds the minimum slope difference
index_min_dif = np.argmin(slope_dif)

# Corresponding start index in the offset strain/regular strain/stress
start_lower = start_index[index_min_dif]
start_upper = start_index[index_min_dif + 1]
# Prints out the lower and upper index in the stress/offset strain data that will be start points for finding a linear
# region
# print("Lower", start_lower, " Upper", start_upper)


# Calculates mimimum and maximum slope by going plus and minus 12% of the average slop of the two most similar slopes
average_min_dif_slope = (slopes_LSR[index_min_dif] + slopes_LSR[index_min_dif + 1]) / 2
min_tol = average_min_dif_slope - 0.12 * average_min_dif_slope
# print("MIN TOL", min_tol)
max_tol = average_min_dif_slope + 0.12 * average_min_dif_slope
# print("MAX TOL:", max_tol)

lower_linear = 0
upper_linear = 0
# Setting lower limit
for i in range(index_min_dif - 1, 0, -1):
    if (slopes_LSR[i] >= min_tol and slopes_LSR[i] <= max_tol):
        lower_linear = start_index[i - 1]
        # print("Lower linear", lower_linear)
    else:
        break

# Setting upper limit
# Setting lower limit
for i in range(index_min_dif + 2, len(slopes_LSR) - 1):
    if (slopes_LSR[i] >= min_tol and slopes_LSR[i] <= max_tol):
        upper_linear = start_index[i - 1]
        # print("Upper Linear", upper_linear)
    else:
        break

# Now to calculate the final 0.2% offset
# This uses the entire range determined as linear to calculate a LSR line and at the end prints out the equation
linear_stress = []
linear_strain = []
print("lower, upper", lower_linear, upper_linear)
for values in range(lower_linear, upper_linear):
    linear_strain.append(strain_offset[values])
    linear_stress.append(stress[values])
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(linear_strain, linear_stress)
print("y = ", slope, 'x +', intercept)

# Creates empty arrays which will hold datapoints for the offset line. Could not figure out how to graph a line that is
# another future work
lsr_strain_offset = []
lsr_predicted_stress = []
# Not an ideal solution to get range for which the line should be created but is easy to adjust and can be changed if
# its too large or small of a range to show in the intercept point
# Also does not go down all the way, this would require me to make data values in this range which I have not done
# There is a more ideal solution somewhere
for index in range(upper_linear + lower_linear + 50):
    x_var = strain_offset[index]
    # print(x_var)
    lsr_predicted_stress.append((slope * x_var) + intercept)
    lsr_strain_offset.append(x_var)

# Plots the stress strain curve and the 0.002% offset curve
plt.plot(strain, stress)
plt.plot(lsr_strain_offset, lsr_predicted_stress)
plt.xlabel('Strain')
plt.ylabel('Stress (ksi)')
plt.title('Stress Vs. Strain with 0.002% offset line')
# Displays Plot, code will pause until plot is closed
plt.show()

# Next we want to find where the predicted stress is the closest to the measured stress - the intercept
# Find absolute value of all differences between actual and predicted
# Find minimum, get actual stress value there
# This is the yield stress method below

# calculates the difference between the offset stress and the measuered stress. Once the smallest stress difference is
# found, the index of this stress is noted
# returns the measuered stress at the index of the minumum difference
# Starts at max index because we know this intersection will occur after the linear section is passed
# Cannot use the data calculated for the offset line because the strain values do not match at the same index
def yield_stress(slope, measuered_stress):
    min_diff = np.absolute((slope * 0 + intercept) - measuered_stress[0])
    min_index = 0
    for index in range(upper_linear, len(stress) - 1):  # Go through offset as this will be shorter
        cur_diff = np.absolute((slope * strain[index] + intercept) - measuered_stress[index])
        if cur_diff < min_diff:
            # print(cur_diff)
            min_diff = cur_diff
            min_index = index
    # print(min_index)
    return measuered_stress[min_index]

# Calls yield_stress to calculate the 0.002% offset yeild stress value
offset_yield_stress = yield_stress(slope, stress)
print('offset yield:', offset_yield_stress)


# Calculate Ultimate tensile strength and returns index it occurs at
# This is just the maximum stress value
def UTS():
    max = stress[0]
    max_index = 0
    for i in range(1, len(stress) - 1):
        if stress[i] > max:
            max = stress[i]
            max_index = i
    return max_index

print("UTS: ", stress[UTS()])
