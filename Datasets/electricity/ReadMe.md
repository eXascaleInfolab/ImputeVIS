As the files are too large for vcs,
the files need to be exported by yourself and then the utils.py needs to be run 
to generate the files and obfuscate the data.

The file is within Utils_Thesis, `utils.py`
```python
    split_file_lines(os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets', 'electricity', 'raw_matrices'))
```