#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_K 5
#define MAX_N (MAX_K*MAX_K)
#define MAX_MOVES 100000 

/* Directions */
static const int DR[4] = {0,  0, -1, 1};   /* LEFT, RIGHT, UP, DOWN — movement of blank (0) */
static const int DC[4] = {-1, 1,  0, 0};
static const char *DIRNAME[4] = {"LEFT", "RIGHT", "UP", "DOWN"};  /* printed names */

/* State */
static int k;                 /* board size k x k */
static int N;                 /* cells = k*k */
static int start[MAX_N];
static int goal_pos_r[MAX_N], goal_pos_c[MAX_N]; /* goal positions for each tile value (0..N-1), zero included */
static int goal[MAX_N];      

static int path[MAX_MOVES];  
static int path_len;


static inline int idx(int r, int c) { return r * k + c; }


static int heuristic(const int *board) {
    int h = 0;
    for (int i = 0; i < N; ++i) {
        int v = board[i];
        if (v == 0) continue; 
        int r = i / k, c = i % k;
        int gr = goal_pos_r[v], gc = goal_pos_c[v];
        int dr = r - gr; if (dr < 0) dr = -dr;
        int dc = c - gc; if (dc < 0) dc = -dc;
        h += dr + dc;
    }
    return h;
}

/* Check solvability for goal with blank at (0,0) (top-left).
   Compute inversions by reading tiles row-wise, not including 0.
   For goal at top-left, solvability differs from the standard bottom-right case.
   Derivation:
   - Let inv = inversion count.
   - Let r0 = row index (0-based from top) of blank.
   - For this goal, the parity condition is:
       * If k is odd:      (inv % 2 == 0)  => solvable
       * If k is even:     ((inv + r0) % 2 == 0) => solvable
*/
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
    for (int i = 0; i < N; ++i) if (board[i] == 0) { blank_idx = i; break; }
    int r0 = blank_idx / k; /* 0-based from top */

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
        /* Solved */
        return 1;
    }

    /* Try moves; avoid reversing previous move */
    for (int dir = 0; dir < 4; ++dir) {
        /* do not reverse: LEFT<->RIGHT, UP<->DOWN */
        if (prev_dir != -1) {
            if ((prev_dir == 0 && dir == 1) || (prev_dir == 1 && dir == 0) ||
                (prev_dir == 2 && dir == 3) || (prev_dir == 3 && dir == 2)) {
                continue;
            }
        }
        int nr = zr + DR[dir], nc = zc + DC[dir];
        if (nr < 0 || nr >= k || nc < 0 || nc >= k) continue;

        /* swap blank with target */
        int zi = idx(zr, zc), ni = idx(nr, nc);
        int tmp = board[ni];
        board[zi] = tmp;
        board[ni] = 0;

        path[path_len++] = dir;
        int found = dfs(board, nr, nc, g + 1, bound, dir);
        if (found) return 1;
        path_len--;

        /* undo swap */
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

    /* Quick solved check */
    int solved = 1;
    for (int i = 0; i < N; ++i) {
        if (start[i] != goal[i]) { solved = 0; break; }
    }
    if (solved) {
        printf("0\n");
        return 0;
    }

    /* Solvability check */
    if (!is_solvable(start)) {
        
        printf("0\n");
        return 0;
    }

    
    int board[MAX_N];
    memcpy(board, start, sizeof(int) * N);

    /* Locate blank */
    int zr = -1, zc = -1;
    for (int i = 0; i < N; ++i) {
        if (board[i] == 0) { zr = i / k; zc = i % k; break; }
    }

    int bound = heuristic(board);
    path_len = 0;

    /* Iterative deepening on bound=f=g+h */
    for (;;) {
        best_over = INT_MAX;
        int found = dfs(board, zr, zc, 0, bound, -1);
        if (found) {
            /* Output result */
            printf("%d\n", path_len);
            for (int i = 0; i < path_len; ++i) {
                printf("%s\n", DIRNAME[path[i]]);
            }
            break;
        }
        if (best_over == INT_MAX) {
            /* No progress possible */
            printf("0\n");
            break;
        }
        bound = best_over;
        /* Loop continues with larger bound */
    }

    return 0;
}
