#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>

#define PATH_MAX_LEN 512

static const char *powercap_root(void) {
    const char *env = getenv("RAPL_POWERCAP_ROOT");
    return env ? env : "/sys/class/powercap";
}

static int read_u64(const char *path, unsigned long long *out) {
    FILE *f = fopen(path, "r");
    if (!f) {
        return -1;
    }
    const int ok = fscanf(f, "%llu", out) == 1;
    fclose(f);
    return ok ? 0 : -1;
}

static unsigned long long max_energy_range = 0;

static void powercap_init(void) {
    char path[PATH_MAX_LEN];
    char name[64];

    snprintf(path, sizeof(path), "%s/intel-rapl:0/name", powercap_root());
    FILE *f = fopen(path, "r");
    if (!f || fscanf(f, "%63s", name) != 1) {
        fprintf(stderr,
                "Erro: nao foi possivel ler %s. "
                "Verifique se o driver intel_rapl esta carregado.\n",
                path);
        exit(EXIT_FAILURE);
    }
    fclose(f);

    if (strncmp(name, "package", 7) != 0) {
        fprintf(stderr, "Erro: dominio intel-rapl:0 chama-se '%s', esperado 'package-*'.\n", name);
        exit(EXIT_FAILURE);
    }

    snprintf(path, sizeof(path), "%s/intel-rapl:0/max_energy_range_uj", powercap_root());
    if (read_u64(path, &max_energy_range) != 0) {
        fprintf(stderr, "Erro ao ler %s\n", path);
        exit(EXIT_FAILURE);
    }

    snprintf(path, sizeof(path), "%s/intel-rapl:0/energy_uj", powercap_root());
    unsigned long long probe;
    if (read_u64(path, &probe) != 0) {
        fprintf(stderr,
                "Erro ao ler %s. "
                "A leitura exige root (execute com sudo).\n",
                path);
        exit(EXIT_FAILURE);
    }

    fprintf(stderr, "Medidor powercap: dominio %s, max_energy_range_uj=%llu\n", name, max_energy_range);
}

static unsigned long long powercap_read(void) {
    char path[PATH_MAX_LEN];
    unsigned long long value;

    snprintf(path, sizeof(path), "%s/intel-rapl:0/energy_uj", powercap_root());
    if (read_u64(path, &value) != 0) {
        fprintf(stderr, "Erro ao ler %s durante a medicao\n", path);
        exit(EXIT_FAILURE);
    }
    return value;
}

/* O contador zera ao passar de max_energy_range_uj; uma execucao nunca dura o
 * suficiente para dar mais de uma volta. */
static double joules_between(unsigned long long before, unsigned long long after) {
    unsigned long long delta;
    if (after >= before) {
        delta = after - before;
    } else {
        delta = after + (max_energy_range - before) + 1;
    }
    return (double)delta * 1e-6;
}

static int env_int(const char *name, int fallback) {
    const char *value = getenv(name);
    if (!value || *value == '\0') {
        return fallback;
    }
    return atoi(value);
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "uso: %s \"<comando>\" <Linguagem> <benchmark>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *command = argv[1];
    const char *language = argv[2];
    const char *test = argv[3];

    const int ntimes = env_int("RAPL_NTIMES", 10);
    const int rest_seconds = env_int("RAPL_REST_SECONDS", 120);

    char path[PATH_MAX_LEN];
    const char *csv_env = getenv("RAPL_CSV");
    if (csv_env && *csv_env != '\0') {
        snprintf(path, sizeof(path), "%s", csv_env);
    } else {
        snprintf(path, sizeof(path), "../%s.csv", language);
    }

    powercap_init();

    fprintf(stderr, "Saida: %s | %d execucoes | descanso de %d s\n", path, ntimes, rest_seconds);

    FILE *fp = fopen(path, "a");
    if (!fp) {
        fprintf(stderr, "Erro ao abrir %s para escrita\n", path);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < ntimes; ++i) {
        struct timeval tvb, tva;

        const unsigned long long energy_before = powercap_read();
        gettimeofday(&tvb, 0);

        const int status = system(command);

        gettimeofday(&tva, 0);
        const unsigned long long energy_after = powercap_read();

        if (status != 0) {
            fprintf(stderr, "Aviso: execucao %d de %s retornou status %d\n", i + 1, test, status);
        }

        const double package = joules_between(energy_before, energy_after);
        double time_spent = (double)(tva.tv_sec - tvb.tv_sec) * 1000000.0 + (double)(tva.tv_usec - tvb.tv_usec);
        time_spent = time_spent / 1000.0;

        /* Colunas do CSV dos autores: benchmark ; package ; core ; gpu ; dram ;
         * tempo(ms). Core, gpu e dram nao existem nesta plataforma. */
        fprintf(fp, "%s ; %.18f ;  ;  ;  ;  %G \n", test, package, time_spent);
        fflush(fp);

        fprintf(stderr, "[%s/%s] execucao %d/%d: %.3f J, %.1f ms\n", language, test, i + 1, ntimes, package, time_spent);

        if (rest_seconds > 0 && i < ntimes - 1) {
            fprintf(stderr, "  descansando %d s\n", rest_seconds);
            fflush(stderr);
            sleep((unsigned)rest_seconds);
        }
    }

    fclose(fp);
    fflush(stderr);
    return EXIT_SUCCESS;
}
