import json
import csv
import argparse
import os

# Default fields for each Yelp dataset
DEFAULT_FIELDS = {
    'review': ['review_id', 'user_id', 'business_id', 'stars', 'text', 'date'],
    'business': ['business_id', 'name', 'address', 'city', 'state', 'postal_code', 'latitude', 'longitude', 'stars', 'review_count', 'is_open', 'categories'],
    'user': ['user_id', 'name', 'review_count', 'yelping_since', 'useful', 'funny', 'cool', 'fans', 'average_stars', 'compliment_hot', 'compliment_more', 'compliment_profile', 'compliment_cute', 'compliment_list', 'compliment_note', 'compliment_plain', 'compliment_cool', 'compliment_funny', 'compliment_writer', 'compliment_photos'],
    'tip': ['user_id', 'business_id', 'text', 'date', 'compliment_count'],
    'checkin': ['business_id', 'date']
}

def guess_file_type(json_path):
    fname = os.path.basename(json_path).lower()
    for key in DEFAULT_FIELDS:
        if key in fname:
            return key
    return 'review'  # fallback

def json_to_csv(json_path, csv_path, fields=None):
    if fields is None:
        file_type = guess_file_type(json_path)
        fields = DEFAULT_FIELDS[file_type]
    with open(json_path, 'r', encoding='utf-8') as fin, open(csv_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.DictWriter(fout, fieldnames=fields)
        writer.writeheader()
        for line in fin:
            data = json.loads(line)
            row = {field: data.get(field, None) for field in fields}
            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Yelp JSON to CSV.")
    parser.add_argument('--input', type=str, required=True, help='Path to input JSON file')
    parser.add_argument('--output', type=str, required=True, help='Path to output CSV file')
    parser.add_argument('--fields', type=str, nargs='+', default=None, help='Fields to extract (default: auto-detect by file type)')
    args = parser.parse_args()

    json_to_csv(args.input, args.output, args.fields)
    print(f"CSV saved to {args.output}") 