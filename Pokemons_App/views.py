from django.shortcuts import render
from django.db import connection
# Create your views here.
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, "index.html")

def query_results(request):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT p1.Generation, p1. Name
        FROM Pokemons p1
        WHERE (p1.HP + p1.Attack + p1.Defense) >= ALL(
            SELECT p2.Attack +p2.Defense + p2.HP
            FROM Pokemons p2
            WHERE p2.Generation = p1.Generation
            ) AND Legendary = 1
        ORDER BY Generation;
        """)
        sql_res1 = dictfetchall(cursor)



