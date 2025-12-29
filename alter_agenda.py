import sqlite3

conn = sqlite3.connect("megatech.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE agenda ADD COLUMN alerta_resolvido INTEGER DEFAULT 0;")
    conn.commit()
    print("✅ Coluna 'alerta_resolvido' adicionada com sucesso.")
except Exception as e:
    print("⚠️ Aviso:", e)

conn.close()
