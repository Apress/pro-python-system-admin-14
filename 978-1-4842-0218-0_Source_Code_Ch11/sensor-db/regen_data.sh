rm monitor.db
sqlite3 -init sample_data.sql monitor.db
./generate-data.py
