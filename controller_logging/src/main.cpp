#include <SDL3/SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

#define MOTION_EVENT_COOLDOWN 40

// CSV Logging
char log_filename[32];
FILE *log_file = NULL;

typedef struct EventMessage {
    char *str;
    Uint64 start_ticks;
    struct EventMessage *next;
} EventMessage;

static EventMessage messages;
static EventMessage *messages_tail = &messages;

// Function to find the next available log filename
void find_next_log_filename(char *filename, size_t size) {
    int count = 0;
    FILE *file;

    while (1) {
        if (count == 0) {
            snprintf(filename, size, "logs/log.csv");
        } else {
            snprintf(filename, size, "logs/log%d.csv", count);
        }

        file = fopen(filename, "r");
        if (!file) {
            return;
        } else {
            fclose(file);
        }
        count++;
    }
}

// CSV Logging function
static void add_message(SDL_JoystickID jid, const char *fmt, ...) {
    EventMessage *msg = NULL;
    char *str = NULL;
    va_list ap;

    msg = (EventMessage *) SDL_calloc(1, sizeof (*msg));
    if (!msg) return;

    va_start(ap, fmt);
    SDL_vasprintf(&str, fmt, ap);
    va_end(ap);
    if (!str) {
        SDL_free(msg);
        return;
    }

    msg->str = str;
    msg->start_ticks = SDL_GetTicks();
    msg->next = NULL;

    messages_tail->next = msg;
    messages_tail = msg;

    // Log to CSV file
    if (log_file) {
        struct timeval tv;
        time_t raw_time;
        struct tm *time_info;
        char time_str[64];

        gettimeofday(&tv, NULL);  // Get current time with microseconds
        raw_time = tv.tv_sec;
        time_info = localtime(&raw_time);
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", time_info);  // Format: YYYY-MM-DD HH:MM:SS

        fprintf(log_file, "%s.%03d,%d,%s\n", time_str, tv.tv_usec / 1000, jid, str);
        fflush(log_file);
    }
}

// Initialize SDL and joystick subsystems, open the log file
SDL_AppResult SDL_AppInit(void **appstate, int argc, char *argv[]) {
    int i;

    SDL_SetAppMetadata("Joystick Input Events", "1.0", "com.example.joystick-events");

    if (SDL_Init(SDL_INIT_JOYSTICK) == 0) {
        SDL_Log("Couldn't initialize SDL: %s", SDL_GetError());
        return SDL_APP_FAILURE;
    }
    

    // Open CSV file
    find_next_log_filename(log_filename, sizeof(log_filename));
    log_file = fopen(log_filename, "w");
    if (log_file) {
        fprintf(log_file, "Timestamp,JoystickID,EventType\n");
        fflush(log_file);
    } else {
        SDL_Log("Failed to open log file!");
    }

    add_message(0, "Please plug in a joystick.");
    return SDL_APP_CONTINUE;
}

// Event handling for joystick events
SDL_AppResult SDL_AppEvent(void *appstate, SDL_Event *event) {
    if (event->type == SDL_EVENT_QUIT) {
        return SDL_APP_SUCCESS;  // End the program successfully
    } else if (event->type == SDL_EVENT_JOYSTICK_ADDED) {
        const SDL_JoystickID which = event->jdevice.which;
        SDL_Joystick *joystick = SDL_OpenJoystick(which);
        if (!joystick) {
            add_message(which, "Joystick #%u added, but not opened: %s", (unsigned int) which, SDL_GetError());
        } else {
            add_message(which, "Joystick #%u ('%s') added", (unsigned int) which, SDL_GetJoystickName(joystick));
        }
    } else if (event->type == SDL_EVENT_JOYSTICK_REMOVED) {
        const SDL_JoystickID which = event->jdevice.which;
        SDL_Joystick *joystick = SDL_GetJoystickFromID(which);
        if (joystick) {
            SDL_CloseJoystick(joystick);  // Joystick unplugged
        }
        add_message(which, "Joystick #%u removed", (unsigned int) which);
    } else if (event->type == SDL_EVENT_JOYSTICK_AXIS_MOTION) {
        static Uint64 axis_motion_cooldown_time = 0;  // Avoid spam, show every X milliseconds
        const Uint64 now = SDL_GetTicks();
        if (now >= axis_motion_cooldown_time) {
            const SDL_JoystickID which = event->jaxis.which;
            axis_motion_cooldown_time = now + MOTION_EVENT_COOLDOWN;
            add_message(which, "Joystick #%u axis %d -> %d", (unsigned int) which, (int) event->jaxis.axis, (int) event->jaxis.value);
        }
    } else if ((event->type == SDL_EVENT_JOYSTICK_BUTTON_UP) || (event->type == SDL_EVENT_JOYSTICK_BUTTON_DOWN)) {
        const SDL_JoystickID which = event->jbutton.which;
        add_message(which, "Joystick #%u button %d -> %s", (unsigned int) which, (int) event->jbutton.button, event->jbutton.down ? "PRESSED" : "RELEASED");
    }
    return SDL_APP_CONTINUE;  // Continue running
}

// Cleanup when the application ends
void SDL_AppQuit(void *appstate, SDL_AppResult result) {
    if (log_file) fclose(log_file);
}

int main(int argc, char *argv[]) {
    void *appstate = NULL;
    SDL_AppResult result = SDL_AppInit(&appstate, argc, argv);

    if (result != SDL_APP_CONTINUE) {
        return 1;  // Failed to initialize
    }

    SDL_Event event;
    while (1) {
        while (SDL_PollEvent(&event)) {
            result = SDL_AppEvent(appstate, &event);
            if (result == SDL_APP_SUCCESS) {
                SDL_AppQuit(appstate, result);
                return 0;
            }
        }
    }
}
