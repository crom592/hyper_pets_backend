import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from support.models import LegalCode

class Command(BaseCommand):
    help = 'Import legal codes from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file containing legal codes')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        # Open the CSV file with utf-8-sig encoding to handle BOM
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # Debug: Print header names to verify they are correct
            print(f"CSV 헤더: {reader.fieldnames}")

            for row in reader:
                # Ensure keys are stripped of whitespace
                row = {key.strip(): value.strip() if value else None for key, value in row.items()}

                # Parse dates
                created_date = row.get('생성일')
                created_date = datetime.strptime(created_date, '%Y%m%d').date() if created_date else None

                abolished_date = row.get('폐지일')
                abolished_date = datetime.strptime(abolished_date, '%Y%m%d').date() if abolished_date else None

                last_updated_date = row.get('최종작업일')
                last_updated_date = datetime.strptime(last_updated_date, '%Y%m%d').date() if last_updated_date else None

                # Save to database
                LegalCode.objects.update_or_create(
                    code=row['법정동코드'],
                    defaults={
                        'name': row['법정동명'],
                        'parent_code': row['상위지역코드'],
                        'rank': int(row['서열']) if row['서열'] else None,
                        'created_date': created_date,
                        'abolished_date': abolished_date,
                        'last_updated_date': last_updated_date,
                        'is_lowest_level': row['최하지역명'] == row['법정동명'],
                        'resident_code': row['법정동코드(주민)'],
                        'cadastral_code': row['법정동코드(지적)'],
                    }
                )
        self.stdout.write(self.style.SUCCESS('Legal codes imported successfully!'))