/* Lossless recording segments through Mesen's public recording API only.
 * No emulated state, input, memory or registers are accessed here.
 */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <string.h>

typedef struct {
    int32_t codec;
    uint32_t compression;
    unsigned char system_hud;
    unsigned char input_hud;
} RecordAviOptions;
typedef void (__stdcall *RecordFn)(char *, RecordAviOptions);
typedef void (__stdcall *StopFn)(void);
typedef unsigned char (__stdcall *ActiveFn)(void);
typedef void (__stdcall *WaveFn)(char *);
static unsigned int segment_index;

/* Optional host-filesystem guard. No emulated state or input is accessed. */
#define CAPTURE_LONG_PATH 32767u
static int capture_budget_blocked;

/* 0 absent, 1 present (including empty), -1 API/allocation failure. */
static int budget_env(const wchar_t *name, wchar_t **value) {
    DWORD n, got, error;
    *value = NULL;
    SetLastError(ERROR_SUCCESS);
    n = GetEnvironmentVariableW(name, NULL, 0);
    error = GetLastError();
    if (!n && error == ERROR_ENVVAR_NOT_FOUND) return 0;
    if (!n && error != ERROR_SUCCESS) return -1;
    if (n > CAPTURE_LONG_PATH) { SetLastError(ERROR_FILENAME_EXCED_RANGE); return -1; }
    *value = (wchar_t *)calloc(n ? n : 1, sizeof(wchar_t));
    if (!*value) { SetLastError(ERROR_NOT_ENOUGH_MEMORY); return -1; }
    if (!n) return 1;
    got = GetEnvironmentVariableW(name, *value, n);
    if (!got || got >= n) { free(*value); *value = NULL; SetLastError(ERROR_INVALID_DATA); return -1; }
    return 1;
}

static int budget_number(const wchar_t *text, uint64_t maximum, uint64_t *out) {
    uint64_t n = 0;
    if (!text || !*text) return 0;
    for (; *text; ++text) {
        unsigned int digit;
        if (*text < L'0' || *text > L'9') return 0;
        digit = (unsigned int)(*text - L'0');
        if (n > maximum / 10 || (n == maximum / 10 && digit > maximum % 10)) return 0;
        n = n * 10 + digit;
    }
    if (!n) return 0;
    *out = n;
    return 1;
}

static wchar_t *budget_join(const wchar_t *left, const wchar_t *right) {
    size_t a = wcslen(left), b = wcslen(right), slash = a && left[a - 1] != L'\\';
    wchar_t *out;
    if (a + slash + b + 1 > CAPTURE_LONG_PATH) { SetLastError(ERROR_FILENAME_EXCED_RANGE); return NULL; }
    out = (wchar_t *)malloc((a + slash + b + 1) * sizeof(wchar_t));
    if (!out) { SetLastError(ERROR_NOT_ENOUGH_MEMORY); return NULL; }
    memcpy(out, left, a * sizeof(wchar_t));
    if (slash) out[a++] = L'\\';
    memcpy(out + a, right, (b + 1) * sizeof(wchar_t));
    return out;
}

/* Canonical extended drive/UNC form. Reject device namespaces. */
static wchar_t *budget_path(const wchar_t *input) {
    wchar_t *plain = NULL, *full = NULL, *out = NULL;
    const wchar_t *source;
    size_t n, i, prefix;
    DWORD needed, got;
    if (!input || !(n = wcslen(input)) || n >= CAPTURE_LONG_PATH) { SetLastError(ERROR_INVALID_NAME); return NULL; }
    plain = (wchar_t *)malloc((n + 3) * sizeof(wchar_t));
    if (!plain) { SetLastError(ERROR_NOT_ENOUGH_MEMORY); return NULL; }
    memcpy(plain, input, (n + 1) * sizeof(wchar_t));
    for (i = 0; i < n; ++i) if (plain[i] == L'/') plain[i] = L'\\';
    source = plain;
    if (!_wcsnicmp(plain, L"\\\\?\\UNC\\", 8)) {
        memmove(plain + 2, plain + 8, (n - 7) * sizeof(wchar_t));
        plain[0] = plain[1] = L'\\';
    } else if (!wcsncmp(plain, L"\\\\?\\", 4)) {
        if (n < 7 || plain[5] != L':' || plain[6] != L'\\') { SetLastError(ERROR_INVALID_NAME); goto done; }
        source += 4;
    } else if (!wcsncmp(plain, L"\\\\.\\", 4)) { SetLastError(ERROR_INVALID_NAME); goto done; }
    needed = GetFullPathNameW(source, 0, NULL, NULL);
    if (!needed || needed > CAPTURE_LONG_PATH) goto done;
    full = (wchar_t *)malloc(needed * sizeof(wchar_t));
    if (!full) { SetLastError(ERROR_NOT_ENOUGH_MEMORY); goto done; }
    got = GetFullPathNameW(source, needed, full, NULL);
    if (!got || got >= needed) { SetLastError(ERROR_INVALID_NAME); goto done; }
    if (got >= 3 && full[1] == L':' && full[2] == L'\\') prefix = 4;
    else if (got >= 5 && full[0] == L'\\' && full[1] == L'\\') prefix = 6;
    else { SetLastError(ERROR_INVALID_NAME); goto done; }
    if (got + prefix + 1 > CAPTURE_LONG_PATH) { SetLastError(ERROR_FILENAME_EXCED_RANGE); goto done; }
    out = (wchar_t *)malloc((got + prefix + 1) * sizeof(wchar_t));
    if (!out) { SetLastError(ERROR_NOT_ENOUGH_MEMORY); goto done; }
    if (prefix == 4) {
        memcpy(out, L"\\\\?\\", 4 * sizeof(wchar_t));
        memcpy(out + 4, full, (got + 1) * sizeof(wchar_t));
        if (out[4] >= L'a' && out[4] <= L'z') out[4] -= L'a' - L'A';
    } else {
        memcpy(out, L"\\\\?\\UNC\\", 8 * sizeof(wchar_t));
        memcpy(out + 8, full + 2, (got - 1) * sizeof(wchar_t));
    }
    n = wcslen(out);
    while (n > 7 && out[n - 1] == L'\\') out[--n] = 0;
done:
    { DWORD error = GetLastError(); free(plain); free(full); SetLastError(error); }
    return out;
}

/* Validate path components rather than following a reparse ancestor. */
static int budget_plain_directory(wchar_t *path) {
    size_t i = 7, n = wcslen(path);
    DWORD attr;
    if (!_wcsnicmp(path, L"\\\\?\\UNC\\", 8)) {
        wchar_t *server = wcschr(path + 8, L'\\');
        wchar_t *share = server ? wcschr(server + 1, L'\\') : NULL;
        if (!server || !server[1]) { SetLastError(ERROR_INVALID_NAME); return 0; }
        i = share ? (size_t)(share - path) : n;
    }
    for (; i <= n; ++i) {
        wchar_t saved;
        if (i != n && path[i] != L'\\') continue;
        saved = path[i]; path[i] = 0;
        attr = GetFileAttributesW(path);
        path[i] = saved;
        if (attr == INVALID_FILE_ATTRIBUTES) return 0;
        if (!(attr & FILE_ATTRIBUTE_DIRECTORY) || (attr & FILE_ATTRIBUTE_REPARSE_POINT)) {
            SetLastError(ERROR_REPARSE_TAG_INVALID); return 0;
        }
    }
    return 1;
}

static int budget_scan(const wchar_t *path, uint64_t *used, DWORD *error, unsigned int depth) {
    HANDLE directory = INVALID_HANDLE_VALUE, find = INVALID_HANDLE_VALUE;
    BY_HANDLE_FILE_INFORMATION info;
    WIN32_FIND_DATAW data;
    wchar_t *pattern = NULL;
    int ok = 0;
    if (depth > 256) { *error = ERROR_STACK_OVERFLOW; return 0; }
    /* Holding each ancestor without write/delete sharing prevents replacement
       while FindFirst/Next follows its path. Unknown sharing errors deny. */
    directory = CreateFileW(path, FILE_LIST_DIRECTORY | FILE_READ_ATTRIBUTES, FILE_SHARE_READ,
        NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, NULL);
    if (directory == INVALID_HANDLE_VALUE) { *error = GetLastError(); goto done; }
    if (!GetFileInformationByHandle(directory, &info)) { *error = GetLastError(); goto done; }
    if (!(info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) || (info.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT)) {
        *error = ERROR_REPARSE_TAG_INVALID; goto done;
    }
    pattern = budget_join(path, L"*");
    if (!pattern) { *error = GetLastError(); goto done; }
    find = FindFirstFileW(pattern, &data);
    if (find == INVALID_HANDLE_VALUE) {
        *error = GetLastError();
        if (*error == ERROR_FILE_NOT_FOUND) { *error = ERROR_SUCCESS; ok = 1; }
        goto done;
    }
    for (;;) {
        if (wcscmp(data.cFileName, L".") && wcscmp(data.cFileName, L"..") &&
            !(data.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT)) {
            if (data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
                wchar_t *child = budget_join(path, data.cFileName);
                int child_ok;
                if (!child) { *error = GetLastError(); goto done; }
                child_ok = budget_scan(child, used, error, depth + 1);
                free(child);
                if (!child_ok) goto done;
            } else {
                uint64_t bytes = ((uint64_t)data.nFileSizeHigh << 32) | data.nFileSizeLow;
                if (data.dwFileAttributes & FILE_ATTRIBUTE_DEVICE) { *error = ERROR_INVALID_DATA; goto done; }
                if (*used > UINT64_MAX - bytes) { *error = ERROR_ARITHMETIC_OVERFLOW; goto done; }
                *used += bytes;
            }
        }
        if (!FindNextFileW(find, &data)) {
            *error = GetLastError();
            if (*error != ERROR_NO_MORE_FILES) goto done;
            *error = ERROR_SUCCESS; ok = 1; break;
        }
    }
done:
    free(pattern);
    if (find != INVALID_HANDLE_VALUE && !FindClose(find)) { if (ok) *error = GetLastError(); ok = 0; }
    if (directory != INVALID_HANDLE_VALUE && !CloseHandle(directory)) { if (ok) *error = GetLastError(); ok = 0; }
    return ok;
}

static int budget_marker(const wchar_t *directory, const char *reason, DWORD error,
                         uint64_t used, uint64_t reserve, uint64_t cap) {
    wchar_t *path;
    HANDLE file;
    char json[512];
    DWORD written;
    int n, ok = 0;
    if (!directory || !*directory || !budget_plain_directory((wchar_t *)directory)) return 0;
    path = budget_join(directory, L"capture-budget-stop.json");
    if (!path) return 0;
    file = CreateFileW(path, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_NEW,
                       FILE_ATTRIBUTE_NORMAL | FILE_FLAG_WRITE_THROUGH | FILE_FLAG_OPEN_REPARSE_POINT, NULL);
    if (file == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        DWORD attr = GetFileAttributesW(path);
        /* Preserve a previous regular marker rather than overwriting evidence. */
        ok = (error == ERROR_FILE_EXISTS || error == ERROR_ALREADY_EXISTS) &&
             attr != INVALID_FILE_ATTRIBUTES && !(attr & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT));
        free(path); return ok;
    }
    free(path);
    n = snprintf(json, sizeof(json),
        "{\"format\":1,\"reason\":\"%s\",\"win32Error\":%lu,\"usedBytes\":%llu,"
        "\"reserveBytes\":%llu,\"capBytes\":%llu,\"segmentIndex\":%u}\n",
        reason, (unsigned long)error, (unsigned long long)used,
        (unsigned long long)reserve, (unsigned long long)cap, segment_index);
    if (n > 0 && (size_t)n < sizeof(json) && WriteFile(file, json, (DWORD)n, &written, NULL) &&
        written == (DWORD)n && FlushFileBuffers(file)) ok = 1;
    if (!CloseHandle(file)) ok = 0;
    return ok;
}

static int budget_deny(const char *reason, DWORD error, const wchar_t *directory,
                       uint64_t used, uint64_t reserve, uint64_t cap) {
    HMODULE core = GetModuleHandleW(L"MesenCore.dll");
    StopFn avi = core ? (StopFn)GetProcAddress(core, "AviStop") : NULL;
    StopFn wave = core ? (StopFn)GetProcAddress(core, "WaveStop") : NULL;
    int marker;
    capture_budget_blocked = 1;
    if (avi) avi();
    if (wave) wave();
    marker = budget_marker(directory, reason, error, used, reserve, cap);
    fprintf(stderr, "CAPTURE BUDGET STOP: reason=%s error=%lu used=%llu reserve=%llu cap=%llu marker=%d\n",
        reason, (unsigned long)error, (unsigned long long)used,
        (unsigned long long)reserve, (unsigned long long)cap, marker);
    fflush(stderr);
    /* This DLL is for the runner's own headless child. Never allow a missing
       marker or missing public stop API to leave an unattended writer alive. */
    if (!marker || !avi || !wave) ExitProcess(86);
    return 0;
}

static int capture_budget_allow(void) {
    static const wchar_t *names[] = { L"SMB_CAPTURE_WORKSPACE", L"SMB_CAPTURE_CAP_BYTES",
        L"SMB_CAPTURE_SEGMENT_FRAMES", L"SMB_CAPTURE_FRAME_LIMIT" };
    wchar_t *values[4] = {NULL, NULL, NULL, NULL}, *raw_dir = NULL, *root = NULL, *directory = NULL;
    int present[4], configured = 0, i, result = 0;
    uint64_t cap = 0, frames = 0, limit = 0, used = 0, reserve = 0;
    DWORD error = ERROR_INVALID_DATA;
    const char *reason = "configuration";
    if (capture_budget_blocked) return 0;
    for (i = 0; i < 4; ++i) { present[i] = budget_env(names[i], &values[i]); configured |= present[i] != 0; }
    if (!configured) { result = 1; goto done; } /* Original calibration no-op. */
    if (budget_env(L"SMB_CAPTURE_SEGMENT_DIR", &raw_dir) != 1 || !(directory = budget_path(raw_dir))) goto deny;
    for (i = 0; i < 4; ++i) if (present[i] != 1) goto deny;
    if (!budget_number(values[1], UINT64_MAX, &cap) ||
        !budget_number(values[2], 1024, &frames) || !budget_number(values[3], 100000, &limit)) goto deny;
    root = budget_path(values[0]);
    if (!root) goto deny;
    /* Exact canonical-case prefix is intentionally conservative on Windows
       case-sensitive directories; the runner supplies the same root spelling. */
    { size_t n = wcslen(root);
      if (wcsncmp(root, directory, n) || (directory[n] && root[n-1] != L'\\' && directory[n] != L'\\')) {
          reason = "segment-outside-workspace"; goto deny;
      }
    }
    if (!budget_plain_directory(root) || !budget_plain_directory(directory)) { error = GetLastError(); reason = "directory-error"; goto deny; }
    reserve = frames * UINT64_C(262144) + limit * UINT64_C(8192) + UINT64_C(536870912);
    if (!budget_scan(root, &used, &error, 0)) { reason = "scan-error"; goto deny; }
    if (used > cap || reserve > cap - used) { error = ERROR_DISK_FULL; reason = "over-budget"; goto deny; }
    { wchar_t *marker = budget_join(directory, L"capture-budget-stop.json");
      DWORD attr;
      if (!marker) { reason = "marker-path"; error = GetLastError(); goto deny; }
      attr = GetFileAttributesW(marker); error = GetLastError(); free(marker);
      if (attr != INVALID_FILE_ATTRIBUTES) { reason = "existing-marker"; error = ERROR_FILE_EXISTS; goto deny; }
      if (error != ERROR_FILE_NOT_FOUND) { reason = "marker-path"; goto deny; }
    }
    result = 1;
    goto done;
deny:
    result = budget_deny(reason, error, directory, used, reserve, cap);
done:
    for (i = 0; i < 4; ++i) free(values[i]);
    free(raw_dir); free(root); free(directory);
    return result;
}


static void start_segment(void) {
    if (!capture_budget_allow()) return;
    HMODULE core = GetModuleHandleW(L"MesenCore.dll");
    const char *directory = getenv("SMB_CAPTURE_SEGMENT_DIR");
    RecordFn record = core ? (RecordFn)GetProcAddress(core, "AviRecord") : NULL;
    ActiveFn active = core ? (ActiveFn)GetProcAddress(core, "AviIsRecording") : NULL;
    char path[32768];
    if (!record || !active || !directory || !*directory) {
        fprintf(stderr, "SEGMENT ERROR: missing public API or output directory\n");
        fflush(stderr);
        return;
    }
    int n = snprintf(path, sizeof(path), "%s/part-%04u.avi", directory, segment_index++);
    if (n < 0 || (size_t)n >= sizeof(path)) {
        fprintf(stderr, "SEGMENT ERROR: output path too long\n");
        fflush(stderr);
        return;
    }
    RecordAviOptions options = {1, 6, 0, 0};
    record(path, options);
    fprintf(stderr, "SEGMENT START: active=%u path=%s\n", active(), path);
    fflush(stderr);
}

static void stop_segment(void) {
    HMODULE core = GetModuleHandleW(L"MesenCore.dll");
    StopFn stop = core ? (StopFn)GetProcAddress(core, "AviStop") : NULL;
    if (!stop) return;
    Sleep(30);
    stop();
    fprintf(stderr, "SEGMENT STOP\n");
    fflush(stderr);
}

__declspec(dllexport) int luaopen_segment_start(void *state) {
    (void)state;
    segment_index = 0;
    start_segment();
    return 0;
}

__declspec(dllexport) int luaopen_segment_next(void *state) {
    (void)state;
    stop_segment();
    start_segment();
    return 0;
}

__declspec(dllexport) int luaopen_segment_stop(void *state) {
    (void)state;
    stop_segment();
    return 0;
}

/* Independent continuous PCM stream: rotating AVI drops an audio block while
 * its recorder waits for the first video frame. Never rotate the WaveRecorder.
 * Public exports: nesdev-org/MesenCE/InteropDLL/RecordApiWrapper.cpp.
 */
__declspec(dllexport) int luaopen_segment_wave_start(void *state) {
    (void)state;
    if (capture_budget_blocked) return 0;
    HMODULE core = GetModuleHandleW(L"MesenCore.dll");
    WaveFn record = core ? (WaveFn)GetProcAddress(core, "WaveRecord") : NULL;
    ActiveFn active = core ? (ActiveFn)GetProcAddress(core, "WaveIsRecording") : NULL;
    const char *directory = getenv("SMB_CAPTURE_SEGMENT_DIR");
    char path[32768];
    if (!record || !active || !directory || !*directory ||
        snprintf(path, sizeof(path), "%s/native-audio.wav", directory) >= (int)sizeof(path)) {
        fprintf(stderr, "SEGMENT ERROR: missing Wave API or valid output path\n");
        fflush(stderr);
        return 0;
    }
    record(path);
    fprintf(stderr, "WAVE START: active=%u path=%s\n", active(), path);
    fflush(stderr);
    return 0;
}

__declspec(dllexport) int luaopen_segment_wave_stop(void *state) {
    (void)state;
    HMODULE core = GetModuleHandleW(L"MesenCore.dll");
    StopFn stop = core ? (StopFn)GetProcAddress(core, "WaveStop") : NULL;
    if (stop) stop();
    fprintf(stderr, "WAVE STOP\n");
    fflush(stderr);
    return 0;
}
