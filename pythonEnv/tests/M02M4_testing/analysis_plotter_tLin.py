# analysis_plotter_tLin.py

"""
Created by: David Smith & Michelle Pichardo
Helper file containing useful functions for files running both pins
- Extract time and voltage
- Plotters
- Analysis 
"""
import matplotlib.pyplot as plt 
import numpy as np

def extract_time_and_voltage(infile, 
                             delimiter=',', 
                             samples_to_av = 1):
    """
    Parameter: File
    Returns: 
    - Time in microseconds starting at zero
    - Voltage: 
        V = (digital value/samples averaged) * (3.3/4096)
        - V0: Volts from A0
        - V1: Volts from A1
        - The value 4096 depends on analog resolution set to 12 bits
    - Samples averaged
        - extracted from file or returns default value 1 
    """
    
    # Read the file to determine the number of header lines and extract parameters
    with open(infile, 'r') as file:
        header_lines = 0
        for line in file:
            header_lines += 1
            # Check if the line contains two columns of numbers separated by a comma
            try:
                float_values = [float(val) for val in line.strip().split(delimiter)]
                if len(float_values) == 4:
                    header_lines -= 1
                    # It's a data line; break from the loop
                    break
            except ValueError:
                # Not a line with two columns of numbers; continue reading headers
                pass

            # Check if "number of samples averaged" is in the header
            if ':' in line:
                param_name, param_value = map(str.strip, line.split(':'))
                if param_name.lower() == 'samples averaged':
                    samples_to_av = int(param_value)


    # extract time and digital value
    t1, t2, d0, d1 = np.genfromtxt(infile, skip_header=header_lines, unpack=True, delimiter=delimiter)

    t = (t2 - t1)/samples_to_av + t1
    # convert digital to voltage 
    #   (digital sample / number of samples averaged) * (3.3/4096)
    v0 = (d0/samples_to_av)*(3.3/4096)
    v1 = (d1/samples_to_av)*(3.3/4096)

    # set time to start at zero 
    t = t - t[0]

    return t, t1, t2, v0, v1, samples_to_av


def quickLook(infile, 
              delimiter=',', 
              samples_to_av = 1): 

    """
    Parameter: File 
    Returns: Scatter plot and histogram of gaps 
    """
    # Default unless overwritten 
    samples_to_av=1
    # Read the file to determine the number of header lines and extract parameters
    with open(infile, 'r') as file:
        header_lines = 0
        for line in file:
            header_lines += 1
            # Check if the line contains two columns of numbers separated by a comma
            try:
                float_values = [float(val) for val in line.strip().split(',')]
                if len(float_values) == 4:
                    header_lines -= 1
                    # It's a data line; break from the loop
                    break
            except ValueError:
                # Not a line with two columns of numbers; continue reading headers
                pass

            # Check if "number of samples averaged" is in the header
            if ':' in line:
                param_name, param_value = map(str.strip, line.split(':'))
                if param_name.lower() == 'samples averaged':
                    samples_to_av = int(param_value)


    # extract time and digital value
    t1, t2, d0, d1 = np.genfromtxt(infile, skip_header=header_lines, unpack=True, delimiter=delimiter)

    t = (t1 + t2)/2 

    # Make a list of the time differences (gaps) between adjacent points:
    dt = t - np.roll(t,1)
    # skip 1st value
    dt = dt[1:]
    h,tax = np.histogram(dt,range=[0,max(dt)],bins=int(max(dt)/100.))

    ## KEEP POST PROCESSING HERE -------------------
    # convert digital to voltage 
    #   (digital sample / number of samples averaged) * (3.3/4096)
    v0 = (d0/samples_to_av)*(3.3/4096)
    v1 = (d1/samples_to_av)*(3.3/4096)

    # set time to start at zero 
    t = t - t[0]
    # convert us to s 
    t = t/1e6
    ##  -------------------

    #plot dataset
    
    fig, axs = plt.subplots(3)
    fig.set_size_inches(8,6)

    axs[0].scatter(t,v0,s=4)
    axs[0].plot(t,v0,alpha=0.5, label ='A0')
    axs[0].set_xlabel('Time (seconds)')
    axs[0].set_ylabel('Volts')
    axs[0].legend()

    axs[1].scatter(t,v1,s=4, color ='C1')
    axs[1].plot(t,v1,alpha=0.5, color ='C1', label= 'A1')
    axs[1].set_xlabel('Time (seconds)')
    axs[1].set_ylabel('Volts')
    axs[1].legend()

    #plot histogram of gaps in milliseconds:
    axs[2].plot(tax[1:]/1e3,h,alpha=0.5)
    axs[2].scatter(tax[1:]/1e3,h,s=4)
    axs[2].set_yscale('log')
    axs[2].set_xlabel('Gap (milliseconds)')
    axs[2].set_ylabel('Count')
    axs[2].grid()

    fig.suptitle(f'{infile}, Samples Av:{samples_to_av}')
    fig.subplots_adjust(top=.93)
    fig.tight_layout()
    plt.show() 

    return 


def analyze(infile, 
            samples_to_av = 1, 
            inter_sample_delay = None,
            inter_average_delay = None,
            gap_sizeL_us = 500., 
            gap_sizeS_us =500., 
            delimiter=',', 
            loc_prints= False, 
            prints=False):

    """
    Parameter: File 
    Optional parameters: 
        - gap_sizeL_us: largest gap size of interest in (us)
        - gap_sizeS_us: smallest gap size of interest in (us)
        - loc_prints: bool, this prints additional info regarding gap locations/durations
        - prints: bool, this prints values for 1 file
    Returns: 
        - dictionary of values
            - samples averaged default/input
            - sample freq
            - median gap
            - large gap default/input
            - count of long gaps
            - largest gap
            - small gap default/input
            - sum of durations larger than small gap 
            - time length of file in ms,s
            - dead time percentage
    """
    # Default unless overwritten 
    # samples_to_av=1
    # inter_sample_delay = None
    # inter_average_delay = None
    # Read the file to determine the number of header lines and extract parameters
    with open(infile, 'r') as file:
        header_lines = 0
        for line in file:
            header_lines += 1
            # Check if the line contains two columns of numbers separated by a comma
            try:
                float_values = [float(val) for val in line.strip().split(',')]
                if len(float_values) == 4:
                    header_lines -= 1
                    # It's a data line; break from the loop
                    break
            except ValueError:
                # Not a line with two columns of numbers; continue reading headers
                pass

            # Check if the line contains parameters
            if ':' in line:
                param_name, param_value = map(str.strip, line.split(':'))
                if param_name.lower() == 'samples averaged':
                    samples_to_av = int(param_value)
                # Uncomment and modify the following lines if other parameters are present
                elif param_name.lower() == 'inter-sample gap (us)':
                    inter_sample_delay = float(param_value)
                elif param_name.lower() == 'inter-average gap (us)':
                    inter_average_delay = float(param_value)


    # extract time and digital value
    t1, t2, d0, d1 = np.genfromtxt(infile, skip_header=header_lines, unpack=True, delimiter=delimiter)
    
    t = (t1 + t2)/2

    # Make a list of the time differences (gaps) between adjacent points:
    dt = t - np.roll(t,1)
    # skip 1st value
    dt = dt[1:]

    ## KEEP POST PROCESSING HERE -------------------
    # convert digital to voltage 
    #   (digital sample / number of samples averaged) * (3.3/4096)
    v0 = (d0/samples_to_av)*(3.3/4096)
    v1 = (d1/samples_to_av)*(3.3/4096)

    # set time to start at zero 
    t = t - t[0]
    # convert to ms
    tms = t/1e3
    # convert us to s 
    ts = t/1e6
    ##  -------------------

    ### Prints ###

    # Sample Frequency 
    #  num of samples/1s = (1 sample/ gap us) *(1us/10^-6)
    #  gap: amount of time taken per sample stored 
    #  old: sample_freq = (1/np.median(dt))*(1e6)
    
    sample_freq = (len(t)/t[-1])*(1e6)
    if prints == True: 
        print(f'Sample Frequency from Median gap (KHz): {sample_freq/1e3:.2f}')

    # Gaps
    if prints == True: 
        print('Median gap (us): ', np.median(dt))
    if prints == True: 
        print(f"\nLARGE GAP ANALYSIS: {gap_sizeL_us/1e3:.0f} ms")

    gap_index_L = np.where(dt > gap_sizeL_us)
    gap_index_L=gap_index_L[0]

    if loc_prints == True: 
        print('Locations of long gaps: ', gap_index_L)
        print('Times of long gaps (ms): ',ts[gap_index_L])
        print('Durations of long gaps (ms): ',dt[gap_index_L]/1e3)

    if prints == True: 
        print('Count of long gaps: ',len(dt[gap_index_L]))
    if prints == True: 
        print('Largest gaps (ms): ',max(dt[gap_index_L])/1e3)

    if prints == True: 
        print(f"\nSMALL GAP ANALYSIS: {gap_sizeS_us/1e3:.0f} ms")

    gap_index_S = np.where(dt > gap_sizeS_us)
    gap_index_S = gap_index_S[0]
    sum_small_gaps = np.sum(dt[gap_index_S])
    sum_small_gaps_ms = np.sum(dt[gap_index_S])/1e3

    if prints == True: 
        print(f"Sum of durations larger than {gap_sizeS_us/1e3:.0f} ms (ms): {sum_small_gaps_ms:.2f}")

    if prints == True: 
        print('\nFile info & Dead Time')
    tot_len_file = t[-1]
    if prints == True: 
        print(f"Time Length of file (ms,s): {tot_len_file/1e3:.2f} , {tot_len_file/1e6:.2f}")

    dead_time = (sum_small_gaps/tot_len_file)*100
    if prints == True: 
        print(f'Dead time = (sum durations > {gap_sizeS_us/1e3:.0f} ms/Time length of file)')
        print(f'Dead time %: {dead_time:.3f} \n')

    # Theoretical Frequency 
    cycle = samples_to_av * inter_sample_delay + inter_average_delay
    theoretical_freq = 1e-3/(cycle*1e-6)

    # Store to dictionary ----
    results_dict = {} 
    results_dict['Samples_Averaged'] = samples_to_av
    results_dict['Inter_Sample_delay'] = inter_sample_delay
    results_dict['Inter_Average_delay'] = inter_average_delay
    results_dict['Theoretical_Frequency_KHz'] = round(theoretical_freq,3)
    results_dict['Sample_Frequency_KHz'] = round(sample_freq / 1e3,3)
    results_dict['Large_Gap_selected_ms'] = gap_sizeL_us / 1e3
    results_dict['Small_Gap_selected_ms'] = gap_sizeS_us / 1e3
    results_dict['Median_Gap_us'] = round(np.median(dt),2)
    results_dict['Count_of_gaps_larger_than_Large_Gap'] = len(dt[gap_index_L])
    results_dict['Largest_Gaps_ms'] = round(max(dt) / 1e3,2)
    # results_dict['Largest_Gaps_ms'] = round(max(dt[gap_index_L]) / 1e3,2)
    results_dict['Smallest_Gap_ms'] = round(min(dt) / 1e3,2)
    results_dict['Sum_of_Durations_Larger_than_Small_Gap_ms'] = round(sum_small_gaps_ms,2)
    results_dict['Time_Length_of_File_ms'] =  round(tot_len_file / 1e3,3)
    results_dict['Time_Length_of_File_s'] =  round(tot_len_file / 1e6,3)
    results_dict['Dead_Time_Percentage'] =  round(dead_time,3)

    return results_dict

