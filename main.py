import sys
import threading
from claim_bonus import load_channel_points_context
from exceptions import StreamerDoesNotExistException
from login import check_login
from pubsub import listen_for_channel_points
from twitch_data import set_streamer_logins, get_channel_id, do_for_each_streamer
from watch_minute import send_minute_watched_events


def main():
    if not check_login():
        print("Ingreso Fallido.")
        return
    streamer_logins = read_streamer_logins()
    if not streamer_logins:
        print("Tienes que especificar al menos un streamer!")
        return
    set_streamer_logins(streamer_logins)
    do_for_each_streamer(load_channel_points_context)
    start_watching()
    listen_for_channel_points()


# Read streamer logins from command-line arguments, if possible. Otherwise, prompt user input.
def read_streamer_logins():
    user_input = []
    if len(sys.argv) <= 1:  # no command-line args (the first is always source file name)
        print("Ingresa el nombre del streamer (o varios streamers separados por comas). Los streamers mas importantes van primero.")
        twitch_streamers = input("Nombres de los streamers: ")
        user_input = twitch_streamers.split(",")
    else:
        for i in range(1, len(sys.argv)):
            user_input += sys.argv[i].split(",")

    streamer_logins = []
    for streamer_login in user_input:
        streamer_login = streamer_login.strip()
        if not streamer_login:
            continue
        try:
            get_channel_id(streamer_login)
        except StreamerDoesNotExistException:
            print(f"El streamer {streamer_login} no existe")
        else:
            streamer_logins.append(streamer_login)
    return streamer_logins


def start_watching():
    minute_watcher_thread = threading.Thread(target=send_minute_watched_events)
    minute_watcher_thread.start()


if __name__ == "__main__":
    main()
