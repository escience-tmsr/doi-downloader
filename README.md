# doi-downloader

## Install

```bash
pip install -r requirements.txt
```

## Run

Create a `.csv` file with the dois you want to download. Dois should be comma seperated. For example:

```csv
10.1109/MIC.2013.3,
10.1109/eScience.2011.40
```

Then run the following command:

```bash
python -m doi_downloader -f path/to/your/file.csv
```
