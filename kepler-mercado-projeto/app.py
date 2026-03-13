from flask import Flask, render_template, request, redirect
import oracledb
import os

app = Flask(__name__)


def get_connection():
    connection = oracledb.connect(
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dsn=os.environ.get("DB_DSN")
    )
    return connection


@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM TB_ATIVOS_GALACTICOS")
    ativos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", ativos=ativos)


@app.route("/processar", methods=["POST"])
def processar():
    evento = request.form["evento"]
    setor = request.form["setor"]

    conn = get_connection()
    cursor = conn.cursor()

    plsql = '''
    DECLARE
        v_evento VARCHAR2(20) := :evento;
        v_setor VARCHAR2(20) := :setor;
        v_novo_preco NUMBER;

        CURSOR c_ativos IS
            SELECT id_ativo, preco_base
            FROM TB_ATIVOS_GALACTICOS
            WHERE setor = v_setor;

    BEGIN

        FOR r IN c_ativos LOOP

            IF v_evento = 'RADIACAO' THEN
                v_novo_preco := r.preco_base * 1.25;

            ELSIF v_evento = 'MINA' THEN
                v_novo_preco := r.preco_base * 0.80;

            ELSE
                v_novo_preco := r.preco_base;

            END IF;

            UPDATE TB_ATIVOS_GALACTICOS
            SET preco_base = v_novo_preco
            WHERE id_ativo = r.id_ativo;

        END LOOP;

        COMMIT;

    END;
    '''

    cursor.execute(plsql, evento=evento, setor=setor)

    cursor.close()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run()