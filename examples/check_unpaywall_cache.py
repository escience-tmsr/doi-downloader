from doi_downloader import unpaywall as upw
import json

# Main function
def main():
    no_of_cached = upw.get_number_of_cached()
    print(f"Number of cached: {no_of_cached}")
    no_404s = upw.get_number_of_cached_404()
    print(f"Number of cached 404s: {no_404s}")
    percentage_404s = no_404s / no_of_cached * 100
    print(f"Percentage of 404s: {percentage_404s:.2f}%")
    dois_with_no_pdf_urls = upw.get_list_with_no_urls()
    for (doi, value, _) in dois_with_no_pdf_urls:
        json_object = json.loads(value)
        if "oa_locations" in json_object:
            if len(json_object["oa_locations"]) > 0:
                print(f'{doi}: {json_object["oa_locations"][0]["url"]}')
                print(f'{doi}: {json_object["oa_locations"][0]["url_for_pdf"]}')
                print('---')
        # else:
        #     print(f'{doi}: No OA locations')
    percentage_no_pdfs = len(dois_with_no_pdf_urls) / no_of_cached * 100
    print(f"Percentage of DOIs with no PDF URLs: {percentage_no_pdfs:.2f}%")

main()
