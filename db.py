import mysql.connector
from mysql.connector import Error, pooling

##banco de dados
DB_PARAMS={
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'imc_pythonfork',
    'charset': 'utf8mb4',
    'time_zone': '-03:00',
    'use_pure': True,
    'connect_timeout': 10
}

##conexões ativas e paradas (5 conexões)
_pool = pooling.MySQLConnectionPool(
    pool_name = 'imc_pool',
    pool_size = 5,
    **DB_PARAMS
)

##conexão com o pool
def get_connection():
    try:
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'erro ao obter uma conexão do pool: {e}')
    

## retorna os dados (lista)
def execute_query(sql, params=None, fetch=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if fetch: 
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount
        
    except Error as e:
        conn.rollback()
        raise Exception(f'erro ao executar error: {e}')
    finally: 
        cursor.close()
        conn.close()

##traz só o resultado (pega o 1 resultado com o 0)(só o objeto)
def execute_one(sql, params=None):
    resultados = execute_query(sql, params, fetch=True)
    return resultados [0] if resultados else None