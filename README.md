# HET_observability

This is a simple tool to plot your targets against available HET queue time in a given trimester

How to do it:

1. clone this repository with:

     ```>>> git clone https://github.com/sjanowiecki/HET_observability/ ```

   Then cd into the directory HET_observability/

2. Compile your target data file with the following columns and save it in a .dat in ascii format such that it is readable by astropy.io.ascii.read:
   - `target_id`: The unique identifier for the target
   - `ra`: Target RA in degrees (J2000)
   - `dec`: Target declination in degrees (J2000)
   - `t_exp`: The requested exposure time
   - [`num_visits`]: The desired amount of visits of the targets.\
      Defaults to 1 if not provided.

3. Now, there are two possible ways to proceed:
   You can...
   - Run the program using\
   ```>>> python -m het_time_calculator.py -h```\
   This will display the help message and list the available arguments.\
   Most importantly, you will need to change the input file name (or save your data in `example_targets.dat`). This will produce a output file of the targets including their expected number of visits, and a plot showing an overview.\
   Or...
   - Import the module into your own script (using `import het_time_calculator as htc`, maybe after appending the path to it to your `sys` path).\
   From here, you can call the calculation pipeline using `htc.perform_all_calculations`, to which you'll have to provide your own `HetTimeCalcConfig` in order to change the parameters, and which will provide you with two astropy Tables that contain enriched information for your targets.

<!-- 
1. Replace the example target data in example_targets.dat with yours.

      RA,Dec(J2000) in decimal degrees, exposure time in seconds, and N visits

2. Edit the beginning of HET_obs.py to set the desired trimester (c_t and c_y).

3. Run HET_obs.py via:

       python HET_obs.py

   which will produce LST_VISITS_PI_20XX-X.pdf.

   This histogram shows the visits required for your targets
      and the available visits for all, grey+dark, and dark time. -->
