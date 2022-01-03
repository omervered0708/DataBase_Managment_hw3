from django.shortcuts import render
from django.db import connection
from .models import Pokemons

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

        cursor.execute("""
        SELECT Pokemons.Name, Pokemons.Type
        FROM Pokemons
        WHERE Pokemons.Name NOT IN (
            -- all pokemon with some pokemon with better stats and same type
            SELECT p1.Name
            FROM Pokemons p1, Pokemons p2
            WHERE p1.Type = p2.Type AND
                  p1.Name <> p2.Name AND
                  (p1.Attack <= p2.Attack OR
                  p1.Defense <= p2.Defense OR
                  p1.HP <= p2.HP))
        ORDER BY Type ASC;
        """)
        sql_res2 = dictfetchall(cursor)
        sql_res3 = None
        if request.method == 'POST' and request.POST:
            X = request.POST["X"]
            Y = request.POST["Y"]
            cursor.execute(f"""
                    SELECT Type
            FROM Pokemons
            GROUP BY Type
            HAVING COUNT(*) > {Y} AND
                MAX(Attack) > {X};
            """)
            sql_res3 = dictfetchall(cursor)

        cursor.execute("""
        SELECT Type, ROUND(AVG(ABS(CAST(Attack - Defense as FLOAT))), 2) as instability
        FROM Pokemons
        GROUP BY Type
        HAVING AVG(ABS(CAST(Attack - Defense as FLOAT))) >= ALL (
            SELECT AVG(ABS(CAST(Attack - Defense as FLOAT)))
            FROM Pokemons
            GROUP BY Type);
        """)
        sql_res4 = dictfetchall(cursor)
        if sql_res3 != None:
            return render(request, 'query_results.html', {'sql_res1': sql_res1,
                                              'sql_res2': sql_res2,
                                              'sql_res3': sql_res3,
                                              'sql_res4': sql_res4,
                                                'X': X, 'Y':Y})
        return render(request, 'query_results.html', {'sql_res1': sql_res1,
                                                      'sql_res2': sql_res2,
                                                      'sql_res4': sql_res4})


    return render(request, 'pokemon_add.html')


def pokemon_add(request):
    if request.method == 'POST' and request.POST:
        # get input
        name = request.POST['name']
        type = request.POST['type']
        generation = request.POST['generation']
        legendary = request.POST['legendary']
        hp = request.POST['HP']
        attack = request.POST['attack']
        defense = request.POST['defense']
        # add pokemon to database
        new_pokemon = Pokemons(name =name,
                               type = type,
                              generation=generation,
                               legendary=legendary,
                               hp = hp,
                               attack = attack,
                               defense=defense
                               )

    return render(request, 'pokemon_add.html')


