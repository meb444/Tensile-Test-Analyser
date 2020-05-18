# Tensile-Test-Analyser
Takes in csv file of tensile data and extracts values. Will eventually create an output file
Tensile Dictionary is the most updated version and will yeild accurate results, at least with all samples I was able to test. 

There is some hard coding for where the actualt data is pulled from the CSV file. For the most part this is clearly commented and could be changed to reflect what rows/cols your data starts in

This code uses KSI and will convert from PSI to KSI by dividing by 1000!
In addition it is assumed all inputted measurments (gugale length, thinkness, ect) are in inches!


Potential issues:
    Lack of clearly defined linear portion may result in an inacurate section chosen to calculate the modulus and offset yeild equation
    Brittle sample may lead to the code calculating the modulus right befor the break, may also produce an offset yeild even if there is not one
    No doubt more as this lacks substansive testing (only 18 samples, all INCONEL 718 produced through AM) - all samples were compared to a hand-performed test using excel and were found to be very close matches & no obvious trend in the error
