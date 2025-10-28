import os
from supabase import create_client, Client

# Cole as suas chaves aqui
SUPABASE_URL = "https://jgyfllmxcdkuzenvhfaf.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpneWZsbG14Y2RrdXplbnZoZmFmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1MjI2MjksImV4cCI6MjA3NzA5ODYyOX0.VWq7KefelN8q-REfNwLvI4DMIo1eGvy-apKTekKSHBI"

# Tenta criar o cliente
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Ligação ao Supabase inicializada com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar o Supabase: {e}")
    supabase = None