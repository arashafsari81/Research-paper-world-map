from csv_processor import CSVProcessor
import pandas as pd

processor = CSVProcessor('/app/APU_publications_2021_2025_cleaned_Final.csv')
processor.load_csv()

# Process just the first few rows to debug
print("Processing first 5 rows...")

# Check the first row in detail
row = processor.df.iloc[0]
print(f"\nFirst row analysis:")
print(f"Title: {row.get('Title', 'N/A')}")

# Extract countries
paper_countries = set()
for i in range(1, 19):
    country_col = f'Country {i}'
    if country_col in row and pd.notna(row[country_col]):
        country = processor.clean_text(row[country_col])
        if country:
            paper_countries.add(country)
            print(f"Found country: {country}")

# Extract universities
paper_universities = []
for i in range(1, 19):
    uni_col = f'University {i}'
    if uni_col in row and pd.notna(row[uni_col]):
        uni = processor.clean_text(row[uni_col])
        if uni:
            paper_universities.append(uni)
            print(f"Found university: {uni}")

# Extract authors
authors_in_paper = []
for i in range(1, 11):
    author_col = f'Author {i}'
    if author_col in row and pd.notna(row[author_col]):
        author_text = processor.clean_text(row[author_col])
        if author_text:
            author_name = processor.extract_author_name(author_text)
            if author_name:
                authors_in_paper.append(author_name)
                print(f"Found author: {author_name}")

# Extract author-affiliation mapping
author_affiliations = {}
for i in range(1, 11):
    affil_col = f'Author with Affliliation {i}'
    if affil_col in row and pd.notna(row[affil_col]):
        affil_text = processor.clean_text(row[affil_col])
        if affil_text:
            author_name, university = processor.parse_affiliation(affil_text)
            if author_name and university:
                author_affiliations[author_name] = university
                print(f"Author-Affiliation: {author_name} -> {university}")

print(f"\nSummary:")
print(f"Countries: {paper_countries}")
print(f"Universities: {paper_universities}")
print(f"Authors: {authors_in_paper}")
print(f"Author-Affiliations: {author_affiliations}")

# Check if authors match affiliations
print(f"\nMatching authors to universities:")
for country in paper_countries:
    for university in paper_universities:
        for author_name in authors_in_paper:
            if author_name in author_affiliations:
                if author_affiliations[author_name] == university:
                    print(f"  {author_name} -> {university} (in {country})")