#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_K 5
#define MAX_N (MAX_K * MAX_K)
#define MAX_MOVES 100000

/* Directions: LEFT, RIGHT, UP, DOWN */
static const int DR[4] = {0, 0, -1, 1};
static const int DC[4] = {-1, 1, 0, 0};
static const char *DIRNAME[4] = {"LEFT", "RIGHT", "UP", "DOWN"};

/* State */
static int k;
static int N;
static int start[MAX_N];
static int goal_pos_r[MAX_N], goal_pos_c[MAX_N];
static int goal[MAX_N];

static int path[MAX_MOVES];
static int path_len;

static inline int idx(int r, int c) {
    return r * k + c;
}

/* Manhattan distance heuristic */
static int heuristic(const int *board) {
    int h = 0;
    for (int i = 0; i < N; ++i) {
        int v = board[i];
        if (v == 0) continue;
        int r = i / k;
        int c = i % k;
        int gr = goal_pos_r[v];
        int gc = goal_pos_c[v];
        int dr = r - gr;
        if (dr < 0) dr = -dr;
        int dc = c - gc;
        if (dc < 0) dc = -dc;
        h += dr + dc;
    }
    return h;
}

/* Solvability check for goal with blank at top-left */
static int is_solvable(const int *board) {
    int inv = 0;
    for (int i = 0; i < N; ++i) {
        if (board[i] == 0) continue;
        for (int j = i + 1; j < N; ++j) {
            if (board[j] == 0) continue;
            if (board[i] > board[j]) inv++;
        }
    }
    int blank_idx = -1;
    for (int i = 0; i < N; ++i) {
        if (board[i] == 0) {
            blank_idx = i;
            break;
        }
    }
    int r0 = blank_idx / k;
    if (k % 2 == 1) {
        return (inv % 2 == 0);
    } else {
        return ((inv + r0) % 2 == 0);
    }
}

/* IDA* search */
static int best_over;

static int dfs(int *board, int zr, int zc, int g, int bound, int prev_dir) {
    int h = heuristic(board);
    int f = g + h;
    if (f > bound) {
        if (f < best_over) best_over = f;
        return 0;
    }
    if (h == 0) {
        return 1;
    }

    for (int dir = 0; dir < 4; ++dir) {
        if (prev_dir != -1) {
            if ((prev_dir == 0 && dir == 1) || (prev_dir == 1 && dir == 0) ||
                (prev_dir == 2 && dir == 3) || (prev_dir == 3 && dir == 2)) {
                continue;
            }
        }
        int nr = zr + DR[dir];
        int nc = zc + DC[dir];
        if (nr < 0 || nr >= k || nc < 0 || nc >= k) continue;

        int zi = idx(zr, zc);
        int ni = idx(nr, nc);
        int tmp = board[ni];
        board[zi] = tmp;
        board[ni] = 0;

        path[path_len++] = dir;
        int found = dfs(board, nr, nc, g + 1, bound, dir);
        if (found) return 1;
        path_len--;

        board[ni] = tmp;
        board[zi] = 0;
    }
    return 0;
}

int main(void) {
    if (scanf("%d", &k) != 1) return 0;
    N = k * k;

    for (int i = 0; i < N; ++i) {
        if (scanf("%d", &start[i]) != 1) return 0;
    }

    for (int i = 0; i < N; ++i) {
        goal[i] = i;
    }
    for (int v = 0; v < N; ++v) {
        goal_pos_r[v] = v / k;
        goal_pos_c[v] = v % k;
    }

    int solved = 1;
    for (int i = 0; i < N; ++i) {
        if (start[i] != goal[i]) {
            solved = 0;
            break;
        }
    }
    if (solved) {
        printf("0\n");
        return 0;
    }

    if (!is_solvable(start)) {
        printf("0\n");
        return 0;
    }

    int board[MAX_N];
    memcpy(board, start, sizeof(int) * N);

    int zr = -1, zc = -1;
    for (int i = 0; i < N; ++i) {
        if (board[i] == 0) {
            zr = i / k;
            zc = i % k;
            break;
        }
    }

    int bound = heuristic(board);
    path_len = 0;

    for (;;) {
        best_over = INT_MAX;
        int found = dfs(board, zr, zc, 0, bound, -1);
        if (found) {
            printf("%d\n", path_len);
            for (int i = 0; i < path_len; ++i) {
                printf("%s\n", DIRNAME[path[i]]);
            }
            break;
        }
        if (best_over == INT_MAX) {
            printf("0\n");
            break;
        }
        bound = best_over;
    }

    return 0;
}
