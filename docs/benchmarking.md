## Testing the plugins

In order to test the performance of the plugins, you need a list of DOIs with the associated names of domains 
where the metadata of the papers are stored, for example: "10.1038/s41586-020-2649-2" and "www.nature.com". 
Place this information in a .csv file with two columns: `doi` and `domain`. Then, assuming that this file is 
called `test.csv`, issue the following command:

```
python -m benchmark.batch_download test.csv
```

This test command will generate information for every plugin that is called and will show the test results, 
for example:

```
============================================================
Total processed: 10
Successful downloads: 6
Success rate: 60.0%
============================================================

Generating benchmark report...
Report generated: benchmark/reports/performance_report.txt
Data exported to: benchmark/reports/performance_data.csv
✓ Reports generated in 'reports/' directory
```

The reports named above, contain more detailed information on the test run, for example: performance per
plugin, performance per journal and combined performance. Note that for efficiency reasons not every plugin 
is called for every DOI. The plugins with names starting later in the alphabet will only be used for DOIs
that the earlier called plugins could not process.
