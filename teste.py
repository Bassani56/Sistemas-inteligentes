import time

# Tamanho do ambiente
ROWS, COLS = 12, 12

# DIREÇÕES na ordem pedida (1..8):
# 1: cima-esquerda, 2: cima, 3: cima-direita,
# 4: esquerda,       X, 5: direita,
# 6: baixo-esquerda, 7: baixo, 8: baixo-direita
direcoes = [
    (-1, -1),  # 1
    (-1,  0),  # 2
    (-1,  1),  # 3
    ( 0, -1),  # 4
    ( 0,  1),  # 5
    ( 1, -1),  # 6
    ( 1,  0),  # 7
    ( 1,  1),  # 8
]

# Sua grade (0 = livre, 1 = obstáculo)
grade = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

visitado = [[False for _ in range(COLS)] for _ in range(ROWS)]
count = 1
def imprimir_grade(grade, visitado):
    """Imprime a grade no terminal: 
       '#' = obstáculo, '.' = livre não visitado, 'V' = visitado
    """
    for i in range(ROWS):
        linha = []
        for j in range(COLS):
            
            if grade[i][j] == 1:
                linha.append('#')
            elif visitado[i][j]:
                global count
                linha.append('V')
                time.sleep(0.02)
                count +=1  
            else:
                linha.append('.')
        print(' '.join(linha))
    print()

def dfs(x, y, delay=0.0, show_map=False):
    """DFS recursivo com 8 direções.
       delay: segundos de pausa entre visitar células (camera lenta).
       show_map: se True, imprime a grade a cada passo.
    """
    # limites
    if x < 0 or y < 0 or x >= ROWS or y >= COLS:
        return

    # já visitado
    if visitado[x][y]:
        return

    # obstáculo
    if grade[x][y] == 1:
        return

    # marca e mostra
    visitado[x][y] = True
    print(f"Visitando ({x}, {y})")
    if show_map:
        imprimir_grade(grade, visitado)

    # pausa para "câmera lenta"
    if delay > 0:
        time.sleep(delay)

    # explora vizinhos na ordem 1..8
    for dx, dy in direcoes:
        nx, ny = x + dx, y + dy
        dfs(nx, ny, delay=delay, show_map=show_map)


# Ponto de início (0,0). Se (0,0) for obstáculo, nada acontece.
start_x, start_y = 0, 0

# Exemplo de uso:
# dfs(start_x, start_y)  # sem pausa
# dfs(start_x, start_y, delay=0.2, show_map=True)  # camera lenta e imprime mapa

if grade[start_x][start_y] == 1:
    print("A posição inicial (0,0) é obstáculo — escolha outro ponto inicial.")
else:
    dfs(start_x, start_y, delay=0.15, show_map=True)
    print("Busca em profundidade finalizada.")
