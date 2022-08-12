import csv
import configparser
from datetime import datetime, timedelta

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')

# Read CSV file and create an dictionary with relevant information
with open(config["Konfiguration"]["CSVInputFile"], 'r', newline='') as csvfile:
    csv_dict_reader = csv.DictReader(csvfile, delimiter=';')
    line_count = 0
    spiele = []
    for row in csv_dict_reader:
        spiele.append(
            {
                "termin": row["Termin"],
                "heim_mannschaft": row["HeimMannschaftName"],
                "gast_mannschaft": row["GastMannschaftName"],
                "heim_mannschaft_nummer": row["HeimMannschaftNummer"],
                "gast_mannschaft_nummer": row["GastMannschaftNummer"],
                "halle": row["Halle"],
            }
        )
        line_count += 1

    print(f'Read {line_count} lines from the CSV file.')

# Create SQL insert statements
sql_rows_insert_pta_sus_sheets = []
sql_rows_insert_pta_sus_tasks = []
pta_sus_sheets_id = 1
pta_sus_tasks_id = 1

for spiel_dict in spiele:

    zu_hause = False
    if config["Konfiguration"]["HeimMannschaft"] in spiel_dict["heim_mannschaft"]:
        zu_hause = True

    mannschaftsnummer = 0
    if zu_hause:
        mannschaftsnummer = spiel_dict['heim_mannschaft_nummer']
    else:
        mannschaftsnummer = spiel_dict['gast_mannschaft_nummer']

    spiel_name = ""
    if zu_hause:
        spiel_name = f"{spiel_dict['heim_mannschaft']} - {spiel_dict['gast_mannschaft']}"
    else:
        spiel_name = f"{spiel_dict['gast_mannschaft']} - {spiel_dict['heim_mannschaft']}"
    
    ort = spiel_dict['heim_mannschaft'].split(" ")[1]
    if spiel_dict["halle"] != "":
        ort += ", " + spiel_dict["halle"]
    
    date_time_obj = datetime.strptime(spiel_dict["termin"], '%d.%m.%Y %H:%M')
    datum = date_time_obj.strftime('%Y-%m-%d')
    uhrzeit_start = date_time_obj.strftime('%I:%M %p')
    uhrzeit_ende = (date_time_obj + timedelta(hours=2.5)).strftime('%I:%M %p')

    mannschaftsfuehrer_name = config["Mannschaft_" + mannschaftsnummer]["Mannschaftsfuehrer"]
    mannschaftsfuehrer_email = config["Mannschaft_" + mannschaftsnummer]["Email"]

    sql_rows_insert_pta_sus_sheets.append(
        f"({pta_sus_sheets_id}, '{spiel_name}', '{datum}', '{datum}', '<p><strong>Ort:</strong> {ort}</p>', 'Single', '', '{mannschaftsfuehrer_name}', '{mannschaftsfuehrer_email}', 'none', 0, 0, 1, 0, 1, 0, 0, 0)"
    )
    
    details = "YES"
    details_required = "NO"
    
    # Frauen
    position = 0
    sql_rows_insert_pta_sus_tasks.append(
        f"({pta_sus_tasks_id}, {pta_sus_sheets_id}, '{datum}', 'Frauen', '{uhrzeit_start}', '{uhrzeit_ende}', 4, '{details}', 'Kommentar', 'NO', 'NO', {position}, '{details_required}', '')"
    )
    pta_sus_tasks_id += 1

    # Männer
    position = 1
    sql_rows_insert_pta_sus_tasks.append(
        f"({pta_sus_tasks_id}, {pta_sus_sheets_id}, '{datum}', 'Männer', '{uhrzeit_start}', '{uhrzeit_ende}', 8, '{details}', 'Kommentar', 'NO', 'NO', {position}, '{details_required}', '')"
    )
    pta_sus_tasks_id += 1

    pta_sus_sheets_id += 1

# Create SQL file
sheets_count = 0
tasks_count = 0

with open(config["Konfiguration"]["SQLOutputFile"], 'w') as writer:

    # Sheets
    writer.write("INSERT INTO `bcw_pta_sus_sheets` (`id`, `title`, `first_date`, `last_date`, `details`, `type`, `position`, `chair_name`, `chair_email`, `sus_group`, `reminder1_days`, `reminder2_days`, `clear`, `clear_days`, `visible`, `trash`, `no_signups`, `duplicate_times`) VALUES\n")
    for row in sql_rows_insert_pta_sus_sheets:
        if(sheets_count > 0):
            writer.write(",\n")
        writer.write(row)
        sheets_count += 1
    writer.write(";\n\n")

    # Tasks
    writer.write("INSERT INTO `bcw_pta_sus_tasks` (`id`, `sheet_id`, `dates`, `title`, `time_start`, `time_end`, `qty`, `need_details`, `details_text`, `allow_duplicates`, `enable_quantities`, `position`, `details_required`, `description`) VALUES\n")
    for row in sql_rows_insert_pta_sus_tasks:
        if(tasks_count > 0):
            writer.write(",\n")
        writer.write(row)
        tasks_count += 1

    writer.write(";\n\n")

print(f'Created {sheets_count} `sheets` and {tasks_count} `tasks` INSERT statements.')
