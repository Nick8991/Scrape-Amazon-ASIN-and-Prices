import sqlite3

# conn = sqlite3.connect('Amazon.db')
# c = conn.cursor()

# Add new column to table
# c.execute('ALTER TABLE Amazon_products ADD COLUMN date_time TEXT')

# Update date_time column with current date and time
# c.execute("UPDATE Amazon_products SET date_time = datetime('now') WHERE EAN = '4012789748895'")

# c.execute(f"SELECT * FROM Amazon_products ORDER BY date_time  DESC LIMIT 1")
# result = c.fetchall()



# conn.commit()
# conn.close()
# print(result[0][0])
EAN_list = []
conn = sqlite3.connect('data//data.db')
c = conn.cursor()
c.execute('SELECT DISTINCT "EAN/GTIN" FROM Alledaten WHERE "EAN/GTIN" IS NOT NULL')
rows = c.fetchall()
for row in rows:
    EAN_list.append(row[0])
set_list = set(EAN_list)
EAN_list = list(set_list) 
print(type(EAN_list[0]))
print(len(EAN_list))