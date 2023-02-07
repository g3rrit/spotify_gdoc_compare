#!/usr/bin/env python

import os
import sys

import argparse
import pandas as pd
import spotipy
import jellyfish


assert sys.version_info.major == 3, "Python2 not supported"


def normalize(ins: str) -> str:
    return ins.lower()


def compare(s1: str, s2: str) -> float:
    return jellyfish.jaro_winkler(normalize(s1), normalize(s2))


def download_doc(url: str, header_col: int) -> str:

    tables = pd.read_html(url, header=header_col)
    assert len(tables) == 1, "Too many tables"
    table = tables[0]

    return table


def get_playlist(playlist_id: str, cid: str, secret: str) -> str:

    client_credentials_manager = spotipy.SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist = sp.playlist_tracks(playlist_id)

    return [{
        "title": track["track"]["name"],
        "artist": track["track"]["artists"][0]["name"]
    } for track in playlist["items"]]


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Spotify Google Doc Compare")

    parser.add_argument("--doc-url", dest="doc_url", type=str, required=True)
    parser.add_argument("--playlist-id", dest="playlist_id", type=str, required=True)
    parser.add_argument("--client-id", dest="client_id", type=str, default=os.getenv("SPOTIFY_CLIENT_ID"))
    parser.add_argument("--secret", dest="secret", type=str, default=os.getenv("SPOTIFY_SECRET"))
    parser.add_argument("--threshold", dest="threshold", type=float, default=0.88)

    return parser.parse_args()


def main():

    args = parse_args()

    assert args.client_id is not None, "Client ID needs to be set"
    assert args.secret is not None, "Secret needs to bet set"

    doc = download_doc(args.doc_url, 9)

    playlist = get_playlist(args.playlist_id, args.client_id, args.secret)

    for track in playlist:

        for _, doc_item in doc.iterrows():

            score = compare(track["title"], doc_item["Title"])

            if score >= args.threshold:
                print(
                    "The following song matches and entry in the doc"
                    f" [{track['title']} - {track['artist']}] [{score:.2f}]"
                )
                print("--------------------")
                print(doc_item["Title"])
                print(doc_item["Version"])
                print(doc_item["What do you think?"])
                print(doc_item["Issues"])
                print(doc_item["Reference"])
                print("====================")


if __name__ == "__main__":
    main()
