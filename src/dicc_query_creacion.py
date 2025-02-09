dicc_query_creacion = {'genero':"""CREATE TABLE IF NOT EXISTS genero (
                                id_genero INT PRIMARY KEY,
                                nombre VARCHAR(100)
                                );""",
                        'type':"""CREATE TABLE IF NOT EXISTS tipo (
                                id_tipo INT PRIMARY KEY,
                                nombre VARCHAR(100)
                                );""",

                        'rol':"""CREATE TABLE IF NOT EXISTS rol (
                                id_rol INT PRIMARY KEY,
                                nombre VARCHAR(100)
                                );""",

                        'peli':"""CREATE TABLE IF NOT EXISTS pelicula (
                                id_pelicula VARCHAR(100) PRIMARY KEY,
                                titulo VARCHAR(100),
                                año INT,
                                puntuacion DECIMAL,
                                duracion DECIMAL
                                );""",
                        'persona': """CREATE TABLE IF NOT EXISTS persona (
                                id_persona INT PRIMARY KEY,
                                nombre VARCHAR(100),
                                año VARCHAR(100),
                                premios DECIMAL,
                                nominaciones DECIMAL
                                );""",
                        'relaciones': """CREATE TABLE IF NOT EXISTS relaciones (
                                id_persona INT,
                                id_pelicula VARCHAR (100),
                                id_tipo INT,
                                id_rol INT,
                                id_genero INT,
                                    FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
                                    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
                                    FOREIGN KEY (id_tipo) REFERENCES tipo(id_tipo)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
                                    FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
                                    FOREIGN KEY (id_genero) REFERENCES genero(id_genero)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE
                                );"""    
    }

dicc_query_insercion = {'genero':'''INSERT INTO "genero" (id,nombre) VALUES (%s,%s)''',
                        'type':'''INSERT INTO "tipo" (id,nombre) VALUES (%s,%s)''',
                        'rol':'''INSERT INTO "rol" (id,nombre) VALUES (%s,%s)''',
                        'peli': '''INSERT INTO "pelicula" (id,titulo,año,puntuacion,duracion) VALUES (%s,%s,%s,%s,%s)''',
                        'persona': '''INSERT INTO "persona" (id,nombre,año,premios,nominaciones) VALUES (%s,%s,%s,%s,%s)'''}