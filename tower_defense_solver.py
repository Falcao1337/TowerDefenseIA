import heapq
import sys
import codecs

def solve_tower_defense(input_file, output_file):
    # Tenta abrir o arquivo com diferentes codificações
    try:
        # Tenta primeiro com UTF-8
        with open(input_file, 'r', encoding='utf-8') as f:
            n = int(f.readline().strip())
            board = []
            for _ in range(n):
                row = f.readline().strip()
                board.append(row)
    except (UnicodeDecodeError, ValueError):
        try:
            # Tenta com UTF-16
            with open(input_file, 'r', encoding='utf-16') as f:
                n = int(f.readline().strip())
                board = []
                for _ in range(n):
                    row = f.readline().strip()
                    board.append(row)
        except (UnicodeDecodeError, ValueError):
            # Última tentativa com detecção automática
            with open(input_file, 'rb') as f:
                raw_data = f.read()
                if raw_data.startswith(codecs.BOM_UTF16):
                    text = raw_data.decode('utf-16')
                else:
                    text = raw_data.decode('utf-8', errors='ignore')
                
                lines = text.splitlines()
                n = int(lines[0].strip())
                board = [line.strip() for line in lines[1:n+1]]
    
    # Encontra as posições das torres
    towers = []
    for i in range(n):
        for j in range(n):
            if board[i][j] == 'T':
                towers.append((i, j))
    
    # Calcula as células atacadas pelas torres
    attacked_cells = {}
    for i in range(n):
        for j in range(n):
            if board[i][j] != 'T':  # Ignora as células com torres
                damage = 0
                for tower_i, tower_j in towers:
                    # Verifica se a célula está adjacente a uma torre (incluindo diagonais)
                    if abs(i - tower_i) <= 1 and abs(j - tower_j) <= 1 and (i, j) != (tower_i, tower_j):
                        damage += 10
                attacked_cells[(i, j)] = damage
    
    # Direções possíveis: Sul, Norte, Leste, Oeste
    directions = [
        (1, 0, 'S'),  # Sul
        (-1, 0, 'N'),  # Norte
        (0, 1, 'L'),  # Leste
        (0, -1, 'O')   # Oeste
    ]
    
    # Algoritmo de Dijkstra para encontrar o caminho com menor dano
    start = (0, 0)
    end = (n-1, n-1)
    
    # Fila de prioridade para Dijkstra: (dano_total, posição_i, posição_j, caminho)
    # Não considera dano na posição inicial
    pq = [(0, start[0], start[1], "")]
    visited = set()
    
    while pq:
        damage, i, j, path = heapq.heappop(pq)
        
        if (i, j) == end:
            # Chegamos ao destino, escreve a solução no arquivo de saída
            with open(output_file, 'w') as f:
                f.write(path)
            return path, damage
        
        if (i, j) in visited:
            continue
        
        visited.add((i, j))
        
        for di, dj, direction in directions:
            ni, nj = i + di, j + dj
            
            # Verifica se a nova posição é válida
            if 0 <= ni < n and 0 <= nj < n and board[ni][nj] != 'T' and (ni, nj) not in visited:
                # Não adiciona dano se for a posição final
                if (ni, nj) == end:
                    new_damage = damage
                else:
                    new_damage = damage + attacked_cells.get((ni, nj), 0)
                new_path = path + direction
                heapq.heappush(pq, (new_damage, ni, nj, new_path))
    
    # Se não encontrar caminho, retorna uma string vazia e dano zero
    with open(output_file, 'w') as f:
        f.write("")
    return "", 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python tower_defense_solver.py instXX.in solXX.out")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    solution, total_damage = solve_tower_defense(input_file, output_file)
    print(f"Solução encontrada: {solution}")
    print(f"Dano total: {total_damage}")