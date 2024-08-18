from pathlib import Path

from anipy_api.anime import Anime
from anipy_api.locallist import LocalList
from anipy_api.provider import get_provider
from anipy_api.player import get_player
from anipy_api.error import LangTypeNotAvailableError

import requests

from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent

from KeywordQueryEventListener import KeywordQueryEventListener
from ItemEnterEventListener import ItemEnterEventListener


class StreamAnime(Extension):

    provider = None
    selected_anime = None
    max_episode = 0
    anime_list = []

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def set_up_provider(self, provider):
        self.provider = get_provider(provider)

    def set_current_anime(self, selected_anime):
        if selected_anime is not None:
            if not isinstance(selected_anime, Anime):
                self.selected_anime = Anime.from_local_list_entry(
                    selected_anime)
                self.selected_anime.language = selected_anime.language
            else:
                self.selected_anime = selected_anime

    def get_current_anime(self):
        return self.selected_anime

    def set_current_anime_max_episode(self, max_episode):
        if max_episode is not None:
            self.max_episode = max_episode

    def get_current_anime_max_episode(self):
        return self.max_episode

    def search_anime(self, search_input, curr_list):
        '''Search the anime using user input'''

        # Clearing the list
        self.anime_list = []

        try:
            # Getting the search data
            animes = self.provider.get_search(search_input)

            if len(animes) > 0:
                for anime in animes:
                    self.anime_list.append(
                        Anime(self.provider,
                              anime.name,
                              anime.identifier,
                              anime.languages)
                    )
            else:
                return None

            return self.show_anime_list(curr_list)
        except requests.exceptions.ConnectionError:
            return "Unable to connect to " + self.provider.BASE_URL
        except Exception as e:
            return str(e)

    #

    def show_anime_list(self, curr_list):
        '''Helps to paginate anime search result'''

        max_item = 10

        if len(self.anime_list) <= max_item:
            return {"animes":  self.anime_list, "next": False}

        if len(self.anime_list) >= max_item * curr_list:
            low = (curr_list - 1) * max_item
            high = low + max_item
            temp_list = self.anime_list[low:high]
            return {"animes": temp_list, "next": True}

        low = (curr_list - 1) * max_item
        temp_list = self.anime_list[low:]
        return {"animes": temp_list, "next": False}

    def get_anime_max_episode_no(self):
        '''Returns the anime latest episode number'''
        try:
            episodes = self.selected_anime.get_episodes(
                lang=self.selected_anime.language)

            if len(episodes) == 0:
                return None

            if len(episodes) == 1:
                self.max_episode = episodes[0]
                return int(episodes[0])

            if len(episodes) > 1:
                self.max_episode = episodes[-1]
                return int(episodes[-1])

            self.max_episode = 1
            return 1

        except ConnectionError:
            return str("Unable to connect to " + self.provider.BASE_URL)
        except Exception as e:
            return str(e)

    def open_episode_in_player(self, episode, player, quality):
        '''Open episode of seleted anime and selected ep no'''
        try:
            player = get_player(
                Path(player),
                extra_args=[]
            )

            stream = self.selected_anime.get_video(
                episode=episode,
                lang=self.selected_anime.language,
                preferred_quality=quality
            )

            if stream is not None:
                player.play_title(self.selected_anime, stream)
                self.write_history(episode)
                return True

            return False
        except LangTypeNotAvailableError:
            return False
        except Exception as e:
            return str(e)

    # History Below

    HISTORY_FOLDER_PATH = Path(Path(__file__).parent) / "history"
    HISTORY_FILE_PATH = HISTORY_FOLDER_PATH / "history.json"

    def write_history(self, current_episode):
        '''Write history to file'''
        local_list = LocalList(Path(self.HISTORY_FILE_PATH))

        local_list.update(self.selected_anime, episode=current_episode,
                          language=self.selected_anime.language)

    def read_history(self, curr_list):
        '''Read history from file'''

        max_item = 15

        local_list = LocalList(Path(self.HISTORY_FILE_PATH))

        animes = local_list.get_all()

        if len(animes) > 0:
            # Sorting based on timestamp to keep the lastest on top
            animes = sorted(animes, key=lambda x: x.timestamp, reverse=True)
        else:
            return None

        if len(animes) <= max_item:
            return {"animes":  animes, "next": False}

        if len(animes) >= max_item * curr_list:
            low = (curr_list - 1) * max_item
            high = low + max_item
            temp_list = animes[low:high]
            return {"animes": temp_list, "next": True}

        if len(animes) - ((curr_list - 1) * max_item) < 0:
            return None

        low = (curr_list - 1) * max_item
        temp_list = animes[low:]

        return {"animes": temp_list, "next": False}

    def delete_item(self, delete_all, anime=None):
        '''Delete single or whole history'''

        local_list = LocalList(Path(self.HISTORY_FILE_PATH))
        if delete_all:
            animes = local_list.get_all()

            for a in animes:
                local_list.delete(a)

        else:
            local_list.delete(anime)


if __name__ == '__main__':
    StreamAnime().run()
