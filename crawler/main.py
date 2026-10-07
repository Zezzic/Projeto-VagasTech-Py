from crawler import remoteok, remotive, weworkremotely
from banco.vagas import criar_indice, salvar_vaga


def coletar():
    criar_indice()

    vagas = remotive.coletar() + weworkremotely.coletar() + remoteok.coletar()

    novas = 0
    repetidas = 0
    for vaga in vagas:
        if salvar_vaga(vaga):
            novas += 1
        else:
            repetidas += 1

    print("Vagas novas salvas:", novas)
    print("Vagas que já existiam:", repetidas)


if __name__ == "__main__":
    coletar()
