# README

Every badminton season, a lot of information about the scheduled matches has to be added to the website.
The script `create_sql_insert_statements.py` generates SQL statements that are used for inserting database entries for the Wordpress plugin "[Volunteer Sign Up Sheets](https://de.wordpress.org/plugins/pta-volunteer-sign-up-sheets/)".

## Preparation

**1. Download Vereinsspielplan as CSV**

https://bwbv-badminton.liga.nu/cgi-bin/WebObjects/nuLigaBADDE.woa/wo/XJkii4ieS7y3XRvYLV4cNM/2.1.0.1.59.0.0.1.19.1.1

**2. Create and modify `config.ini`**

See default values in `config_default.ini`.

## Usage

Execute script:

```sh
python create_sql_insert_statements.py
```

Copy the SQL statements from the output file and execute them (e.g. in phpMyAdmin).
