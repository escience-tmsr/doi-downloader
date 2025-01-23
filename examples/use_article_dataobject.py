import jsonschema
from doi_downloader import article_dataobject as ado

# Example usage
data = {
    "message": {
        "title": ["Sample Article Title"],
        "author": [
            {"given": "John", "family": "Doe"},
            {"given": "Jane", "family": "Smith"}
        ],
        "DOI": "10.1038/s41586-019-1666-5",
        "publisher": "Nature Publishing Group",
        "issued": {"date-parts": [[2023, 12, 1]]},
        "link": [
            {"URL": "https://example.com/article.pdf", "content-type": "application/pdf"}
        ]
    }
}

# Create a ArticleDataObject instance
json_data = ado.ArticleDataObject(data)

# Validate the Article data
try:
    if json_data.validate():
        print("Article data is valid.")
except jsonschema.exceptions.ValidationError:
    print("Validation failed.")

# Output the Article data as a string
print(json_data.to_json())
